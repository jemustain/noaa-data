"""
Script to search for weather stations near Tucson, AZ
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NOAA_API_KEY = os.getenv('NOAA_API_KEY')
BASE_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2'

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)


def get_headers():
    """Return headers with API token"""
    return {'token': NOAA_API_KEY}


def search_stations(location_id=None, dataset_id='GHCND', limit=100):
    """
    Search for weather stations
    
    Args:
        location_id (str): Location ID (e.g., 'FIPS:04019' for Pima County, AZ)
        dataset_id (str): Dataset ID to filter stations
        limit (int): Maximum number of results
        
    Returns:
        list: Station information
    """
    url = f'{BASE_URL}/stations'
    
    params = {
        'datasetid': dataset_id,
        'limit': limit,
        'sortfield': 'name'
    }
    
    if location_id:
        params['locationid'] = location_id
    
    response = requests.get(url, headers=get_headers(), params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error searching stations: {response.status_code}")
        print(response.text)
        return []


def search_locations(location_category='CITY', limit=100):
    """
    Search for locations
    
    Args:
        location_category (str): Category (CITY, CNTRY, ST, etc.)
        limit (int): Maximum number of results
        
    Returns:
        list: Location information
    """
    url = f'{BASE_URL}/locations'
    
    params = {
        'locationcategoryid': location_category,
        'limit': limit,
        'sortfield': 'name'
    }
    
    response = requests.get(url, headers=get_headers(), params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error searching locations: {response.status_code}")
        print(response.text)
        return []


def main():
    """Main execution function"""
    print("=" * 60)
    print("NOAA Station Search for Tucson, AZ Area")
    print("=" * 60)
    
    # Verify API key is loaded
    if not NOAA_API_KEY:
        print("ERROR: NOAA_API_KEY not found in environment variables!")
        print("Please make sure .env file exists with your API key.")
        return
    
    # Search for Pima County stations (Tucson is in Pima County)
    print("\nSearching for weather stations in Pima County, AZ...")
    print("Location ID: FIPS:04019 (Pima County)")
    
    stations = search_stations(location_id='FIPS:04019', limit=50)
    
    if stations:
        print(f"\nFound {len(stations)} stations:")
        print("-" * 60)
        
        for i, station in enumerate(stations, 1):
            print(f"\n{i}. {station.get('name', 'N/A')}")
            print(f"   ID: {station.get('id', 'N/A')}")
            print(f"   Elevation: {station.get('elevation', 'N/A')} m")
            print(f"   Location: {station.get('latitude', 'N/A')}, {station.get('longitude', 'N/A')}")
            print(f"   Min Date: {station.get('mindate', 'N/A')}")
            print(f"   Max Date: {station.get('maxdate', 'N/A')}")
        
        # Save results
        filepath = DATA_DIR / 'tucson_area_stations.json'
        with open(filepath, 'w') as f:
            json.dump(stations, f, indent=2)
        print(f"\n\nStation list saved to: {filepath}")
    else:
        print("No stations found.")
    
    print("\n" + "=" * 60)
    print("Search complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
