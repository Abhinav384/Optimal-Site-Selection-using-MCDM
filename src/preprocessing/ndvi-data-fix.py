import pandas as pd
import json

# Load the dataset
df = pd.read_csv('data/ndvi-data.csv')

# Parse the coordinate from .geo column and store as a tuple (lon, lat)
df['coordinates'] = df['.geo'].apply(lambda x: tuple(json.loads(x)['coordinates']))

# Group by coordinate, date, and hour, then calculate mean NDVI
grouped = df.groupby(['coordinates', 'date', 'hour']).agg({
    'NDVI': 'mean',
    'city': 'first'  # optional: pick first city name in group
}).reset_index()

# Rename columns to match final desired format
grouped.rename(columns={
    'city': 'City',
    'coordinates': 'Coordinate',
    'date': 'Date',
    'hour': 'Hour',
    'NDVI': 'NDVI Values'
}, inplace=True)

# Save or display the result
grouped.to_csv('averaged_ndvi_data.csv', index=False)
print(grouped.head())
