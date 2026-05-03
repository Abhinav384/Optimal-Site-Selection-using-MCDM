// ========== 1. Load Target Coordinates from CSV ==========
var coordCsv = ee.FeatureCollection('projects/ee-abhinavbcs23/assets/Targetted-Coordinates');

// Convert CSV to points
var targetPoints = coordCsv.map(function(feature) {
  var lon = feature.getNumber('Longitude');
  var lat = feature.getNumber('Latitude');
  return ee.Feature(ee.Geometry.Point([lon, lat]), {
    'Combined_Coordinates': feature.get('Combined_Coordinates')
  });
});

// ========== 2. Calculate Aspect from SRTM Elevation ==========
var elevation = ee.Image('USGS/SRTMGL1_003');
var terrain = ee.Terrain.products(elevation); // Calculates slope/aspect
var aspect = terrain.select('aspect'); // Aspect in degrees (0-360)

// ========== 3. Extract Aspect for Each Point ==========
var aspectData = aspect.reduceRegions({
  collection: targetPoints,
  reducer: ee.Reducer.first(),
  scale: 30  // Native SRTM resolution
});

// ========== 4. Format to Match Your Schema (Corrected) ==========
var formattedResults = aspectData.map(function(feature) {
  var coords = feature.geometry().coordinates();
  var aspectDegrees = ee.Number(feature.get('first'));
  
  // Calculate cardinal direction using mathematical approach
  var directionIndex = aspectDegrees.add(22.5).divide(45).floor().mod(8);
  var cardinalDirections = ee.List(['N','NE','E','SE','S','SW','W','NW']);
  var aspectDirection = cardinalDirections.get(directionIndex);
  
  return ee.Feature(null, {
    'City': 'Amritsar',
    'Date': 'Static',
    'Longitude': coords.get(0),
    'Latitude': coords.get(1),
    'Aspect': aspectDegrees,
    'Combined_Coordinates': feature.get('Combined_Coordinates'),
    'Aspect_Cardinal': aspectDegrees.format('%.0f').cat('°'),
    'Aspect_Direction': aspectDirection
  });
});
// ========== 5. Export Results ==========
Export.table.toDrive({
  collection: formattedResults,
  description: 'Amritsar_Aspect_At_Target_Points',
  fileFormat: 'CSV',
  selectors: [
    'City', 'Date', 'Longitude', 'Latitude', 
    'Aspect', 'Aspect_Cardinal', 'Aspect_Direction',
    'Combined_Coordinates'
  ]
});

// ========== 6. Visualization ==========
var aspectViz = {
  min: 0,
  max: 360,
  palette: [
    '#0000FF', '#0080FF', '#00FFFF', '#80FF80',
    '#FFFF00', '#FF8000', '#FF0000', '#800080',
    '#0000FF'  // Full color circle
  ]
};

Map.addLayer(aspect.clip(targetPoints), aspectViz, 'Aspect');
Map.addLayer(targetPoints, {color: 'black'}, 'Target Points');
print('First 5 aspect values:', formattedResults.limit(5));