// Load CSV from Cloud Assets
var csvPoints = ee.FeatureCollection("projects/ee-abhinavbcs23/assets/Targetted-Coordinates");

// Get most recent MODIS land cover image before May 2025
var landcover = ee.ImageCollection("MODIS/006/MCD12Q1")
  .filterDate('2001-01-01', '2025-05-01')
  .sort('system:time_start', false)
  .first();

print("Land Cover Image used:", landcover);

// Select land cover band
var lulc = landcover.select('LC_Type1');

// Lookup dictionary for MODIS class codes
var classDict = ee.Dictionary({
  0: 'Evergreen Needleleaf Forest',
  1: 'Evergreen Broadleaf Forest',
  2: 'Deciduous Needleleaf Forest',
  3: 'Deciduous Broadleaf Forest',
  4: 'Mixed Forests',
  5: 'Closed Shrublands',
  6: 'Open Shrublands',
  7: 'Woody Savannas',
  8: 'Savannas',
  9: 'Grasslands',
  10: 'Permanent Wetlands',
  11: 'Croplands',
  12: 'Urban and Built-Up Lands',
  13: 'Cropland/Natural Vegetation Mosaic',
  14: 'Snow and Ice',
  15: 'Barren or Sparsely Vegetated',
  16: 'Water Bodies',
  254: 'Unclassified',
  255: 'Fill Value'
});

// Function to attach LULC code and name to each point
var addLULC = function(feature) {
  var lc = lulc.sample({
    region: feature.geometry(),
    scale: 500,
    numPixels: 1,
    geometries: true
  });

  var lcCode = ee.Algorithms.If(
    lc.size().gt(0),
    ee.Feature(lc.first()).get('LC_Type1'),
    null
  );

  var lcName = classDict.get(ee.String(ee.Number(lcCode).format()));

  return feature.set({
    'LULC_Class': lcCode,
    'LULC_Name': lcName
  });
};

// Apply function to all points
var pointsWithLULC = csvPoints.map(addLULC);

// Preview
print("Points with LULC and Names:", pointsWithLULC.limit(5));

// Export to Google Drive
Export.table.toDrive({
  collection: pointsWithLULC,
  description: 'LULC_Extraction_With_Names',
  fileFormat: 'CSV'
});
