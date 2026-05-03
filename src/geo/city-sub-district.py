import geopandas as gpd
import pandas as pd
import os
import shutil

def extract_city_with_subdistricts(district_geojson, subdistrict_geojson, city_name="Amritsar", output_folder="city_shapefiles"):
    # Define file paths inside the 'data' folder
    district_geojson = os.path.join("data", district_geojson)
    subdistrict_geojson = os.path.join("data", subdistrict_geojson)

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Load district and sub-district GeoJSON files
    districts_gdf = gpd.read_file(district_geojson)
    subdistricts_gdf = gpd.read_file(subdistrict_geojson)

    # Check which column contains district (city) names
    district_name_col = "dtname" if "dtname" in districts_gdf.columns else districts_gdf.columns[0]
    subdistrict_name_col = "dtname" if "dtname" in subdistricts_gdf.columns else subdistricts_gdf.columns[0]

    # Extract the city (district) geometry
    city_gdf = districts_gdf[districts_gdf[district_name_col] == city_name]

    if city_gdf.empty:
        print(f"Error: City '{city_name}' not found in district-level data.")
        return

    # Extract sub-districts that belong to the city (district)
    subdistricts_in_city = subdistricts_gdf[subdistricts_gdf[subdistrict_name_col] == city_name]

    if subdistricts_in_city.empty:
        print(f"Error: No sub-districts found for city '{city_name}' in sub-district-level data.")
        return

    # Merge city and sub-districts into a single GeoDataFrame
    final_gdf = gpd.GeoDataFrame(pd.concat([city_gdf, subdistricts_in_city], ignore_index=True), crs=districts_gdf.crs)

    # Define output shapefile path
    city_shapefile = os.path.join(output_folder, f"{city_name.replace(' ', '_')}.shp")

    # Save the extracted city with all sub-districts as a shapefile
    final_gdf.to_file(city_shapefile)
    print(f"City shapefile saved at: {city_shapefile}")

    # Zip the folder for easier access
    zip_filename = f"{output_folder}.zip"
    shutil.make_archive(output_folder, 'zip', output_folder)
    print(f"Zipped output available at {zip_filename}")

# Example usage
extract_city_with_subdistricts("PUNJAB_DISTRICTS.geojson", "PUNJAB_SUBDISTRICTS.geojson")