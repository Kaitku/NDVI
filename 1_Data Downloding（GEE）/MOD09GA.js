var roi = ee.FeatureCollection("users/KaitkuSFishhh/HSproject/SYRIVER"); // shp boundary
var batch = require('users/fitoprincipe/geetools:batch');
var oeel=require('users/OEEL/lib:loadAll')

Map.centerObject(roi, 7);
Map.addLayer(roi, {color: "cyan"}, "roi");


var mod = ee.ImageCollection('MODIS/061/MOD09GA')
          .filterDate("2022-01-01", "2023-01-01")
          .filterBounds(roi)
          .map(mask)
          .select(['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03', 'sur_refl_b02', 'sur_refl_b06', 'sur_refl_b07',])
          .map(function(image){return image.clip(roi)});
print("MODIS Original Dataset：", mod);


function mask(image) {
  var QA = image.select('state_1km')
  var bitMask = 1 << 10;
  var normBands = image.select('sur_refl_b.*').multiply(0.0001);
  return image.addBands(normBands, null, true)
  .updateMask(QA.bitwiseAnd(bitMask).eq(0))}


var modis_sg=oeel.ImageCollection.SavatskyGolayFilter(mod,
        ee.Filter.maxDifference(1000*3600*24*16, 'system:time_start', null, 'system:time_start'),
        function(infromedImage,estimationImage){
          return ee.Image.constant(ee.Number(infromedImage.get('system:time_start'))
          .subtract(ee.Number(estimationImage.get('system:time_start'))));},3,
          ['sur_refl_b.*']);
print('after-SG', modis_sg)


print('=============================================================> part 1')


Map.addLayer(
  modis_sg,
  {
    min: 0,
    max: 1,
    region:roi,
    bands: ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'],
  },
  "modis_sg"
);


batch.Download.ImageCollection.toDrive(modis_sg,"MOD09GA_multi_sg",{
  scale:480,
  region:roi,
  type:"float",
  crs: "EPSG:4326",
  dateFormat: 'yyyy-MM-dd'
 })
