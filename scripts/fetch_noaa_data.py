"""
Script to fetch weather data from NOAA API for Tucson, AZ
"""

import os
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NOAA_API_KEY = os.getenv('NOAA_API_KEY')
STATION_ID = os.getenv('STATION_ID', 'GHCND:USW00023160')  # Tucson International Airport
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


def fetch_data(dataset_id, start_date, end_date, station_id, data_types=None, limit=1000):
    """
    Fetch weather data from NOAA API
    
    Args:
        dataset_id (str): Dataset ID (e.g., 'GHCND' for Daily Summaries)
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        station_id (str): Weather station ID
        data_types (list): List of data types to fetch (e.g., ['TMAX', 'TMIN', 'PRCP'])
        limit (int): Maximum number of results to return
        
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
        'units': 'standard'  # Use standard units (Fahrenheit, inches)
    }
    
    if data_types:
        params['datatypeid'] = ','.join(data_types)
    
    all_results = []
    offset = 1
    
    while True:
        params['offset'] = offset
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                break
                
            all_results.extend(results)
            print(f"Fetched {len(all_results)} records...")
            
            # Check if we have more data
            metadata = data.get('metadata', {})
            result_set = metadata.get('resultset', {})
            if result_set.get('offset', 0) + result_set.get('count', 0) >= result_set.get('limit', 0):
                break
            
            offset += limit
        else:
            print(f"Error fetching data: {response.status_code}")
            print(response.text)
            break
    
    return all_results


def save_data(data, filename):
    """
    Save data to JSON file
    
    Args:
        data (dict/list): Data to save
        filename (str): Output filename
    """
    filepath = DATA_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to: {filepath}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("NOAA Data Fetcher for Tucson, AZ")
    print("=" * 60)
    
    # Verify API key is loaded
    if not NOAA_API_KEY:
        print("ERROR: NOAA_API_KEY not found in environment variables!")
        print("Please make sure .env file exists with your API key.")
        return
    
    print(f"\nUsing station: {STATION_ID}")
    
    # Fetch station information
    print("\nFetching station information...")
    station_info = fetch_station_info(STATION_ID)
    if station_info:
        print(f"Station Name: {station_info.get('name', 'N/A')}")
        print(f"Elevation: {station_info.get('elevation', 'N/A')} meters")
        print(f"Location: {station_info.get('latitude', 'N/A')}, {station_info.get('longitude', 'N/A')}")
        save_data(station_info, 'tucson_station_info.json')
    
    # Fetch weather data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nFetching weather data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    # Common data types:
    # TMAX - Maximum temperature
    # TMIN - Minimum temperature
    # PRCP - Precipitation
    # AWND - Average wind speed
    # SNOW - Snowfall
    # SNWD - Snow depth
    
    data_types = ['TMAX', 'TMIN', 'PRCP', 'AWND']
    
    weather_data = fetch_data(
        dataset_id='GHCND',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        station_id=STATION_ID,
        data_types=data_types
    )
    
    if weather_data:
        print(f"\nTotal records fetched: {len(weather_data)}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_data(weather_data, f'tucson_weather_{timestamp}.json')
    else:
        print("No data retrieved.")
    
    print("\n" + "=" * 60)
    print("Data fetch complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
