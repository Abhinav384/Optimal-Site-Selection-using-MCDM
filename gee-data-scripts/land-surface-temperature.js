// 1. Load CSV asset containing Latitude and Longitude columns
var rawTable = ee.FeatureCollection('projects/ee-abhinavbcs23/assets/Targetted-Coordinates');

// 2. Convert CSV fields into point geometries
var points = rawTable.map(function(feature) {
  var lon = ee.Number(feature.get('Longitude'));
  var lat = ee.Number(feature.get('Latitude'));
  var point = ee.Geometry.Point([lon, lat]);
  return ee.Feature(point).copyProperties(feature);
});

// 3. Define time range: May 2024
var startDate = '2024-05-01';
var endDate = '2024-06-01';

// 4. Load MODIS Daily LST ImageCollection (Terra MOD11A1)
var modis = ee.ImageCollection('MODIS/061/MOD11A1')
  .filterDate(startDate, endDate)
  .select('LST_Day_1km');

// 5. MODIS scale factor for LST
var scaleFactor = 0.02;

// 6. Function to sample daily LST at each point
function sampleModisLST(image) {
  var lstCelsius = image.select('LST_Day_1km')
    .multiply(scaleFactor)
    .subtract(273.15)
    .rename('LST');

  var date = image.date().format('YYYY-MM-dd');
  
  return lstCelsius.sampleRegions({
    collection: points,
    scale: 1000,
    geometries: true
  }).map(function(f) {
    return f.set('date', date);
  });
}

// 7. Map the sampling function over daily MODIS images
var modisLST = modis.map(sampleModisLST).flatten();

// 8. Export results to Google Drive
Export.table.toDrive({
  collection: modisLST,
  description: 'MODIS_LST_CSV_Export_May2024',
  folder: 'GEE_LST_Exports',
  fileNamePrefix: 'MODIS_LST_100Points_May2024',
  fileFormat: 'CSV'
});
