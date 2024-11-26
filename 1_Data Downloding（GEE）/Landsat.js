var roi = ee.FeatureCollection("users/KaitkuSFishhh/HSproject/SYRIVER"); // shp boundary
var batch = require('users/fitoprincipe/geetools:batch');
var lib3 = require('users/zhangby/library:timeSeries');

Map.centerObject(roi, 7);
Map.addLayer(roi, {color: "cyan"}, "roi");

// var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
          .filterDate("2022-01-01", "2023-01-01")
          .filterBounds(roi)
          .map(maskL9sr)
          .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7','QA_PIXEL','ST_B10'])
          .map(function(image){return image.clip(roi)});
print("L9 Original Dataset：", l9);


function maskL9sr(image) {
  // Develop masks for unwanted pixels (fill, cloud, cloud shadow).
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);

  // Apply the scaling factors to the appropriate bands.
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);

  return image.addBands(opticalBands, null, true)
      .addBands(thermalBands, null, true)
      .updateMask(qaMask)
      .updateMask(saturationMask)}


print('=============================================================> part 1')


var final_dataset = lib3.temporalAggregate(
  l9.select(['SR_B4', 'SR_B3', 'SR_B2', 'SR_B5', 'SR_B6', 'SR_B7']),'YMD','median')
    .filter(ee.Filter.stringContains("system:index", "_131033_"));
//    .filter(ee.Filter.stringContains("system:index", "_132032_"));
print("L9 Filtered Dataset", final_dataset);


Map.addLayer(
  final_dataset,
  {
    min: 0,
    max: 1,
    region:roi,
    bands: ['SR_B4', 'SR_B3', 'SR_B2'],
  },
  "final_dataset"
);


batch.Download.ImageCollection.toDrive(final_dataset,"L9_multi",{
  scale:30,
  region:roi,
  type:"float",
  crs: "EPSG:4326",
  dateFormat: 'yyyy-MM-dd'
 })
