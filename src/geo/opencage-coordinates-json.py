import pandas as pd
import json
import os
from opencage.geocoder import OpenCageGeocode
from time import sleep

# Configuration
API_KEY = "e6a4ad27065a4f0c9e3a2e8f40f475c7"  # Replace with your actual key
INPUT_CSV = "data/Targetted-Coordinates.csv"
OUTPUT_DIR = "address_results"  # Directory to store JSON files
REQUEST_DELAY = 1  # Seconds between API calls (avoid rate limiting)

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_full_address_details(lat, lon):
    """Get complete address details from coordinates"""
    try:
        results = geocoder.reverse_geocode(lat, lon)
        if not results:
            return {"error": "No results found"}
        
        # Extract all available components
        components = results[0]['components']
        geometry = results[0]['geometry']
        formatted = results[0]['formatted']
        
        # Structure the response data
        address_data = {
            "coordinates": {"latitude": lat, "longitude": lon},
            "formatted_address": formatted,
            "address_components": components,
            "geometry": geometry,
            "confidence": results[0].get('confidence', None),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        return address_data
        
    except Exception as e:
        return {"error": str(e)}

# Initialize geocoder
geocoder = OpenCageGeocode(API_KEY)

# Process CSV
df = pd.read_csv(INPUT_CSV)

for index, row in df.iterrows():
    lat, lon = row['Latitude'], row['Longitude']
    
    print(f"Processing coordinate {index+1}/{len(df)}: {lat}, {lon}")
    
    # Get address data
    address_data = get_full_address_details(lat, lon)
    
    # Save to JSON file
    output_filename = f"coord_{index+1}_{lat}_{lon}.json".replace(".", "_")
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, 'w') as f:
        json.dump(address_data, f, indent=2)
    
    # Respect API rate limits
    sleep(REQUEST_DELAY)

print(f"\nProcessing complete. {len(df)} JSON files saved to '{OUTPUT_DIR}'")