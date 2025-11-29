"""
Script to view and analyze NOAA weather data in a readable format
"""

import json
import glob
from pathlib import Path
from datetime import datetime
import pandas as pd

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'


def find_latest_weather_file():
    """Find the most recent weather data file"""
    weather_files = glob.glob(str(DATA_DIR / 'tucson_weather_*.json'))
    if not weather_files:
        return None
    return max(weather_files)


def load_json_data(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def display_station_info():
    """Display station information"""
    station_file = DATA_DIR / 'tucson_station_info.json'
    if not station_file.exists():
        print("Station info file not found. Run fetch_noaa_data.py first.")
        return
    
    station_info = load_json_data(station_file)
    
    print("=" * 60)
    print("STATION INFORMATION")
    print("=" * 60)
    print(f"Name: {station_info.get('name', 'N/A')}")
    print(f"ID: {station_info.get('id', 'N/A')}")
    print(f"Location: {station_info.get('latitude', 'N/A')}, {station_info.get('longitude', 'N/A')}")
    print(f"Elevation: {station_info.get('elevation', 'N/A')} meters")
    print(f"Data Available: {station_info.get('mindate', 'N/A')} to {station_info.get('maxdate', 'N/A')}")
    print()


def display_weather_summary(data):
    """Display a summary of weather data"""
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Extract date (remove time)
    df['date_only'] = pd.to_datetime(df['date']).dt.date
    
    print("=" * 60)
    print("WEATHER DATA SUMMARY")
    print("=" * 60)
    print(f"Total Records: {len(df)}")
    print(f"Date Range: {df['date_only'].min()} to {df['date_only'].max()}")
    print(f"Data Types: {', '.join(df['datatype'].unique())}")
    print()


def display_daily_weather(data, num_days=10):
    """Display daily weather in a readable table format"""
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['date_only'] = pd.to_datetime(df['date']).dt.date
    
    # Pivot data to have one row per day
    pivot_df = df.pivot_table(
        index='date_only',
        columns='datatype',
        values='value',
        aggfunc='first'
    )
    
    # Sort by date (most recent first)
    pivot_df = pivot_df.sort_index(ascending=False)
    
    print("=" * 80)
    print(f"DAILY WEATHER DATA (Most Recent {num_days} Days)")
    print("=" * 80)
    print()
    
    # Display header
    print(f"{'Date':<12}", end='')
    for col in pivot_df.columns:
        if col == 'TMAX':
            print(f"{'Max Temp (°F)':<15}", end='')
        elif col == 'TMIN':
            print(f"{'Min Temp (°F)':<15}", end='')
        elif col == 'PRCP':
            print(f"{'Precip (in)':<15}", end='')
        elif col == 'AWND':
            print(f"{'Wind (mph)':<15}", end='')
        else:
            print(f"{col:<15}", end='')
    print()
    print("-" * 80)
    
    # Display data
    for idx, (date, row) in enumerate(pivot_df.head(num_days).iterrows()):
        if idx >= num_days:
            break
        print(f"{str(date):<12}", end='')
        for col in pivot_df.columns:
            value = row[col]
            if pd.isna(value):
                print(f"{'N/A':<15}", end='')
            else:
                print(f"{value:<15.2f}", end='')
        print()
    print()


def display_temperature_stats(data):
    """Display temperature statistics"""
    df = pd.DataFrame(data)
    
    # Filter for temperature data
    tmax_df = df[df['datatype'] == 'TMAX']
    tmin_df = df[df['datatype'] == 'TMIN']
    
    if len(tmax_df) == 0 or len(tmin_df) == 0:
        print("No temperature data available.")
        return
    
    print("=" * 60)
    print("TEMPERATURE STATISTICS")
    print("=" * 60)
    print(f"Maximum Temperature:")
    print(f"  Highest: {tmax_df['value'].max():.1f}°F")
    print(f"  Average: {tmax_df['value'].mean():.1f}°F")
    print(f"  Lowest:  {tmax_df['value'].min():.1f}°F")
    print()
    print(f"Minimum Temperature:")
    print(f"  Highest: {tmin_df['value'].max():.1f}°F")
    print(f"  Average: {tmin_df['value'].mean():.1f}°F")
    print(f"  Lowest:  {tmin_df['value'].min():.1f}°F")
    print()


def display_precipitation_stats(data):
    """Display precipitation statistics"""
    df = pd.DataFrame(data)
    
    # Filter for precipitation data
    prcp_df = df[df['datatype'] == 'PRCP']
    
    if len(prcp_df) == 0:
        print("No precipitation data available.")
        return
    
    total_precip = prcp_df['value'].sum()
    days_with_rain = len(prcp_df[prcp_df['value'] > 0])
    
    print("=" * 60)
    print("PRECIPITATION STATISTICS")
    print("=" * 60)
    print(f"Total Precipitation: {total_precip:.2f} inches")
    print(f"Days with Rain: {days_with_rain}")
    print(f"Average per Day: {prcp_df['value'].mean():.3f} inches")
    if days_with_rain > 0:
        print(f"Average on Rainy Days: {prcp_df[prcp_df['value'] > 0]['value'].mean():.2f} inches")
    print()


def export_to_csv(data, output_file='tucson_weather.csv'):
    """Export data to CSV format"""
    df = pd.DataFrame(data)
    df['date_only'] = pd.to_datetime(df['date']).dt.date
    
    # Pivot to have one row per day
    pivot_df = df.pivot_table(
        index='date_only',
        columns='datatype',
        values='value',
        aggfunc='first'
    )
    
    output_path = DATA_DIR / output_file
    pivot_df.to_csv(output_path)
    print(f"✓ Data exported to: {output_path}")
    print()


def main():
    """Main execution function"""
    print("\n")
    print("*" * 60)
    print("NOAA WEATHER DATA VIEWER")
    print("*" * 60)
    print()
    
    # Display station information
    display_station_info()
    
    # Find and load the latest weather data file
    latest_file = find_latest_weather_file()
    
    if not latest_file:
        print("No weather data files found.")
        print("Run 'python scripts\\fetch_noaa_data.py' to fetch data first.")
        return
    
    print(f"Loading data from: {Path(latest_file).name}")
    print()
    
    data = load_json_data(latest_file)
    
    # Display various views of the data
    display_weather_summary(data)
    display_daily_weather(data, num_days=14)
    display_temperature_stats(data)
    display_precipitation_stats(data)
    
    # Export to CSV
    print("=" * 60)
    print("EXPORTING DATA")
    print("=" * 60)
    export_to_csv(data)
    
    print("*" * 60)
    print("View complete!")
    print("*" * 60)
    print()


if __name__ == '__main__':
    main()
