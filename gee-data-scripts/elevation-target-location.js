// ========== 1. Load Target Coordinates from CSV ==========
// Replace with your actual Google Drive CSV file path
var coordCsv = ee.FeatureCollection('projects/ee-abhinavbcs23/assets/Targetted-Coordinates');

// Convert CSV to points (assuming columns are 'Longitude' and 'Latitude')
var targetPoints = coordCsv.map(function(feature) {
  var lon = feature.getNumber('Longitude');
  var lat = feature.getNumber('Latitude');
  return ee.Feature(ee.Geometry.Point([lon, lat]), {
    'Combined_Coordinates': feature.get('Combined_Coordinates') // Preserve original ID
  });
});

print('Elevation Points', targetPoints);


// Display points on map for verification
Map.addLayer(targetPoints, {color: 'FF0000'}, 'Target Points');
Map.centerObject(targetPoints, 10);

// ========== 2. Load SRTM Elevation Data ==========
var elevation = ee.Image('USGS/SRTMGL1_003');

// ========== 3. Extract Elevation for Each Point ==========
var elevationData = elevation.reduceRegions({
  collection: targetPoints,
  reducer: ee.Reducer.first(), // Gets elevation value at each point
  scale: 30  // SRTM native resolution (30m)
});

// ========== 4. Format to Match NDVI Schema ==========
var formattedResults = elevationData.map(function(feature) {
  var coords = feature.geometry().coordinates();
  return ee.Feature(null, { // Null geometry to reduce export size
    'City': 'Amritsar',
    'Date': 'Static', // Elevation doesn't change over time
    'Longitude': coords.get(0),
    'Latitude': coords.get(1),
    'Elevation': feature.get('first'), // Elevation value
    'Combined_Coordinates': feature.get('Combined_Coordinates')
  });
});

// ========== 5. Export Results ==========
print('First 5 elevation points:', formattedResults.limit(5));

Export.table.toDrive({
  collection: formattedResults,
  description: 'Amritsar_Elevation_At_Target_Points',
  fileFormat: 'CSV',
  selectors: ['City', 'Date', 'Longitude', 'Latitude', 'Elevation', 'Combined_Coordinates']
});

// ========== Bonus: Create Elevation Visualization ==========
var elevationViz = {
  min: 200,  // Adjust based on your area
  max: 250,  // Adjust based on your area
  palette: ['blue', 'green', 'brown', 'white']
};

Map.addLayer(elevation.clip(targetPoints), elevationViz, 'Elevation at Points');