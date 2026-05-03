// ========== 1. Load Shapefile ==========
var city = 'Amritsar';
var shapefile = ee.FeatureCollection('projects/ee-abhinavbcs23/assets/Amritsar');
var geometry = shapefile.geometry().simplify(100);

// ========== 2. Set Time Range ==========
var startDate = '2024-05-01';
var endDate = '2024-06-01';
var start = ee.Date(startDate);
var end = ee.Date(endDate);

// ========== 3. Load and Process Sentinel-2 Data ==========
var s2 = ee.ImageCollection('COPERNICUS/S2_SR')
.filterBounds(geometry)
.filterDate(start, end)
.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60));

// Calculate NDVI and add date property
var withNDVI = s2.map(function(image) {
var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
return ndvi
.set('date', date)
.copyProperties(image, ['system:time_start']);
});

// Print number of available images
print('Available Sentinel-2 images:', withNDVI.size());

// ========== 4. Create Daily Time Series with Coordinates ==========
// Generate sequence of days
var nDays = end.difference(start, 'days');
var dayList = ee.List.sequence(0, nDays.subtract(1));
var dates = dayList.map(function(d) {
return start.advance(d, 'days');
});

// Function to extract coordinates from a feature
var addCoordinates = function(feature) {
var point = feature.geometry().coordinates();
return feature.set({
longitude: point.get(0),
latitude: point.get(1)
});
};

// For each day, get the closest available NDVI image
var dailyData = dates.map(function(date) {
var d = ee.Date(date);
var dateStr = d.format('YYYY-MM-dd');

// Find images before or on this day, sorted newest first
var filtered = withNDVI.filter(ee.Filter.lte('date', dateStr))
.sort('system:time_start', false);

return ee.Algorithms.If(
filtered.size().gt(0),
// If images exist, sample the most recent one
filtered.first().sample({
region: geometry,
scale: 100,
numPixels: 500,
geometries: true
}).map(function(f) {
var withCoords = addCoordinates(f);
return withCoords.set({
city: city,
date: dateStr,
image_date: filtered.first().get('date'),
days_diff: d.difference(ee.Date(filtered.first().get('system:time_start')), 'days')
});
}),
// If no images exist, return empty feature with date info
ee.FeatureCollection([ee.Feature(null, {
city: city,
date: dateStr,
NDVI: null,
image_date: null,
days_diff: null,
longitude: null,
latitude: null
})])
);
});

// Flatten the results
var result = ee.FeatureCollection(dailyData).flatten();

// ========== 5. Export Results ==========
print('First 5 days:', result.limit(5));
print('Total days processed:', result.size());

Export.table.toDrive({
collection: result,
description: 'Amritsar_Daily_NDVI_May2024_With_Coords',
fileFormat: 'CSV',
selectors: ['city', 'date', 'NDVI', 'longitude', 'latitude', 'image_date', 'days_diff']
});