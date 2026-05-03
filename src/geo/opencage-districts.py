import pandas as pd
from opencage.geocoder import OpenCageGeocode

# Initialize OpenCage Geocoder
API_KEY = "e6a4ad27065a4f0c9e3a2e8f40f475c7"  # Replace with your actual key
geocoder = OpenCageGeocode(API_KEY)

def get_district_details(lat, lon):
    try:
        results = geocoder.reverse_geocode(lat, lon)
        if not results:
            return "No results found"
        
        components = results[0]['components']
        
        # Try different district-related fields in priority order
        district_fields = [
            'county',           # Common in many countries
            'state_district',   # Used in some regions
            'borough',          # For city boroughs
            'suburb',           # Common in urban areas
            'city_district',    # Alternative field
            'neighbourhood',    # More granular
            'region'            # Fallback
        ]
        
        for field in district_fields:
            if field in components:
                return components[field]
        
        # Fallback to city if no district found
        return components.get('city', 'District information not available')
        
    except Exception as e:
        return f"Geocoding error: {str(e)}"

# Process CSV file
def process_coordinates(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    
    # Verify required columns exist
    required_columns = ['Latitude', 'Longitude']
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Missing required columns: {missing}")
    
    # Process each row
    df['District'] = df.apply(
        lambda row: get_district_details(row['Latitude'], row['Longitude']),
        axis=1
    )
    
    # Save results
    df.to_csv(output_csv, index=False)
    print(f"Processed {len(df)} coordinates. Results saved to {output_csv}")

# Example usage
if __name__ == "__main__":
    input_file = "data/Targetted-Coordinates.csv"
    output_file = "output_with_districts.csv"
    process_coordinates(input_file, output_file)