import gc
import os
import numpy as np
from osgeo import gdal
from Functions import writeTiff, masktif
import time


start = time.time()


def cal_ndvi(file, below, above, band_red=1, band_nir=4):
    if file is None:
        print('Could not open the file ' + file)
    else:
        red = file.GetRasterBand(band_red).ReadAsArray()
        nir = file.GetRasterBand(band_nir).ReadAsArray()
        ndvi = (nir - red) / (nir + red)
        ndvi = ndvi.astype(float)
        ndvi[ndvi <= below] = np.nan
        ndvi[ndvi > above] = np.nan
        del red, nir
        gc.collect()
        return ndvi


if __name__ == '__main__':
    basic = r"H:\SYRiver\L8\basic\2022-132_crops_noncube.tif"
    input_path = r".\input dir"  # folder of input images
    out_path = r".\output dir"  # folder of output images

    path_list = os.listdir(input_path)
    tif_files = list()
    for filename in path_list:
        if os.path.splitext(filename)[1] == '.tif':
            tif_files.append(filename)

    total = len(tif_files)

    for idx, i in enumerate(tif_files, start=1):
        progress = f"{idx}/{total}"
        tif = input_path + '\\' + i
        in_ds = gdal.Open(tif)
        geotransform = in_ds.GetGeoTransform()
        projinfo = in_ds.GetProjection()

        (filepath, fullname) = os.path.split(tif)
        (prename, suffix) = os.path.splitext(fullname)
        out_ds = out_path + '\\' + prename + "-NDVI" + suffix
        ndvi_ds = cal_ndvi(in_ds, 0, 1)
        ndvi_crops = masktif(basic, ndvi_ds, 1, np.nan)
        writeTiff(ndvi_crops, geotransform, projinfo, out_ds)

        print('Process：', progress, '|Fin：', os.path.split(out_ds)[-1])
        del geotransform, projinfo, in_ds, ndvi_ds, ndvi_crops, out_ds
        gc.collect()

    print('Finished! | Total time：', time.time() - a, 's')


