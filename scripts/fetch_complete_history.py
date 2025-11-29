"""
Script to fetch ALL historical weather data from NOAA API for Tucson, AZ
This script will fetch all available data from the station's start date to present.
Due to API rate limits, this may take several minutes.
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configuration
NOAA_API_KEY = os.getenv('NOAA_API_KEY')
STATION_ID = os.getenv('STATION_ID', 'GHCND:USW00023160')
BASE_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2'

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)


def get_headers():
    """Return headers with API token"""
    return {'token': NOAA_API_KEY}


def fetch_station_info(station_id):
    """
    Fetch information about a specific weather station
    
    Args:
        station_id (str): NOAA station ID
        
    Returns:
        dict: Station information
    """
    url = f'{BASE_URL}/stations/{station_id}'
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching station info: {response.status_code}")
        print(response.text)
        return None


def fetch_data_batch(dataset_id, start_date, end_date, station_id, data_types=None, limit=1000):
    """
    Fetch weather data from NOAA API for a specific date range
    
    Args:
        dataset_id (str): Dataset ID (e.g., 'GHCND' for Daily Summaries)
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        station_id (str): Weather station ID
        data_types (list): List of data types to fetch
        limit (int): Maximum number of results per request
        
    Returns:
        list: Weather data records
    """
    url = f'{BASE_URL}/data'
    
    params = {
        'datasetid': dataset_id,
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'limit': limit,
        'units': 'standard'
    }
    
    if data_types:
        params['datatypeid'] = ','.join(data_types)
    
    all_results = []
    offset = 1
    
    while True:
        params['offset'] = offset
        
        # Add small delay to respect rate limits (5 requests per second)
        time.sleep(0.21)
        
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                break
                
            all_results.extend(results)
            
            # Check if we have more data
            metadata = data.get('metadata', {})
            result_set = metadata.get('resultset', {})
            count = result_set.get('count', 0)
            
            if count < limit:
                break
            
            offset += limit
            
        elif response.status_code == 429:
            print("  Rate limit reached, waiting 60 seconds...")
            time.sleep(60)
            continue
        else:
            print(f"  Error fetching data: {response.status_code}")
            print(f"  {response.text}")
            break
    
    return all_results


def fetch_all_historical_data(station_id, data_types, start_year=None):
    """
    Fetch all historical data by breaking it into yearly chunks
    
    Args:
        station_id (str): Weather station ID
        data_types (list): List of data types to fetch
        start_year (int): Starting year (if None, uses station's mindate)
        
    Returns:
        list: All weather data records
    """
    print("Fetching station information...")
    station_info = fetch_station_info(station_id)
    
    if not station_info:
        return []
    
    # Get date range
    min_date_str = station_info.get('mindate', '1946-01-01')
    max_date_str = station_info.get('maxdate', datetime.now().strftime('%Y-%m-%d'))
    
    min_date = datetime.strptime(min_date_str, '%Y-%m-%d')
    max_date = datetime.strptime(max_date_str, '%Y-%m-%d')
    
    if start_year:
        min_date = datetime(start_year, 1, 1)
    
    print(f"Station: {station_info.get('name', 'N/A')}")
    print(f"Data available from: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Total span: {(max_date - min_date).days} days")
    print()
    
    # Fetch data in yearly chunks
    all_data = []
    current_date = min_date
    
    while current_date < max_date:
        # Calculate end date (1 year later or max_date, whichever is earlier)
        end_date = min(
            datetime(current_date.year + 1, 1, 1) - timedelta(days=1),
            max_date
        )
        
        print(f"Fetching data for {current_date.year}... ({current_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        
        batch_data = fetch_data_batch(
            dataset_id='GHCND',
            start_date=current_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            station_id=station_id,
            data_types=data_types
        )
        
        if batch_data:
            all_data.extend(batch_data)
            print(f"  ✓ Retrieved {len(batch_data)} records (Total so far: {len(all_data)})")
        else:
            print(f"  No data for this period")
        
        # Move to next year
        current_date = datetime(current_date.year + 1, 1, 1)
    
    return all_data


def convert_to_csv(json_data, output_file='tucson_weather_complete.csv'):
    """
    Convert JSON weather data to CSV format with one row per day
    
    Args:
        json_data (list): Raw JSON data from NOAA API
        output_file (str): Output CSV filename
        
    Returns:
        pandas.DataFrame: Processed data
    """
    print("\nConverting data to CSV format...")
    
    # Convert to DataFrame
    df = pd.DataFrame(json_data)
    
    if df.empty:
        print("No data to convert!")
        return None
    
    # Extract date (remove time component)
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Pivot data to have one row per day with columns for each data type
    pivot_df = df.pivot_table(
        index='date',
        columns='datatype',
        values='value',
        aggfunc='first'
    )
    
    # Sort by date
    pivot_df = pivot_df.sort_index()
    
    # Save to CSV
    output_path = DATA_DIR / output_file
    pivot_df.to_csv(output_path)
    
    print(f"\n✓ Data saved to: {output_path}")
    print(f"  Total days: {len(pivot_df)}")
    print(f"  Date range: {pivot_df.index.min()} to {pivot_df.index.max()}")
    print(f"  Columns: {', '.join(pivot_df.columns.tolist())}")
    
    return pivot_df


def save_raw_json(data, filename='tucson_weather_complete.json'):
    """
    Save raw JSON data
    
    Args:
        data (list): Data to save
        filename (str): Output filename
    """
    filepath = DATA_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Raw JSON saved to: {filepath}")


def display_summary_stats(df):
    """Display summary statistics of the complete dataset"""
    if df is None or df.empty:
        return
    
    print("\n" + "=" * 60)
    print("COMPLETE DATASET STATISTICS")
    print("=" * 60)
    
    if 'TMAX' in df.columns:
        print(f"\nMaximum Temperature (°F):")
        print(f"  All-time high: {df['TMAX'].max():.1f}")
        print(f"  All-time low:  {df['TMAX'].min():.1f}")
        print(f"  Average:       {df['TMAX'].mean():.1f}")
    
    if 'TMIN' in df.columns:
        print(f"\nMinimum Temperature (°F):")
        print(f"  All-time high: {df['TMIN'].max():.1f}")
        print(f"  All-time low:  {df['TMIN'].min():.1f}")
        print(f"  Average:       {df['TMIN'].mean():.1f}")
    
    if 'PRCP' in df.columns:
        total_precip = df['PRCP'].sum()
        days_with_rain = (df['PRCP'] > 0).sum()
        print(f"\nPrecipitation:")
        print(f"  Total (all years): {total_precip:.2f} inches")
        print(f"  Days with rain:    {days_with_rain}")
        print(f"  Average per day:   {df['PRCP'].mean():.3f} inches")
    
    print("\n" + "=" * 60)


def main():
    """Main execution function"""
    print("=" * 60)
    print("NOAA COMPLETE HISTORICAL DATA FETCHER")
    print("Tucson, AZ - All Available Data")
    print("=" * 60)
    print()
    
    # Verify API key is loaded
    if not NOAA_API_KEY:
        print("ERROR: NOAA_API_KEY not found in environment variables!")
        print("Please make sure .env file exists with your API key.")
        return
    
    print(f"Using station: {STATION_ID}")
    print()
    
    # Ask user if they want to limit the start year
    print("This will fetch ALL historical data, which may take a while.")
    print("The Tucson International Airport station has data since 1946.")
    print()
    response = input("Fetch all data since 1946? (y/n, or enter a start year like 2000): ").strip().lower()
    
    start_year = None
    if response and response != 'y' and response != 'yes':
        try:
            start_year = int(response)
            print(f"Will fetch data starting from year {start_year}")
        except ValueError:
            print("Cancelled.")
            return
    
    print("\n" + "=" * 60)
    print("FETCHING DATA")
    print("=" * 60)
    print("This may take several minutes due to API rate limits...")
    print()
    
    # Data types to fetch
    data_types = ['TMAX', 'TMIN', 'PRCP', 'AWND', 'SNOW', 'SNWD']
    
    # Fetch all historical data
    all_data = fetch_all_historical_data(
        station_id=STATION_ID,
        data_types=data_types,
        start_year=start_year
    )
    
    if not all_data:
        print("\nNo data retrieved. Please check your API key and station ID.")
        return
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL RECORDS FETCHED: {len(all_data)}")
    print(f"{'=' * 60}")
    
    # Save raw JSON
    print("\nSaving data...")
    save_raw_json(all_data)
    
    # Convert to CSV
    df = convert_to_csv(all_data)
    
    # Display statistics
    if df is not None:
        display_summary_stats(df)
    
    print("\n" + "=" * 60)
    print("COMPLETE! All historical data has been fetched and saved.")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
