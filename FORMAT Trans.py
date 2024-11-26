import gc
import os
import numpy as np
from osgeo import gdal
import time


a = time.time()


def writeTiff(array, im_geotrans, im_proj, path):
    driver = gdal.GetDriverByName("GTiff")
    if len(array.shape) == 2:
        dst = driver.Create(path, array.shape[1], array.shape[0], 1, gdal.GDT_Float32)
        dst.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dst.SetProjection(im_proj)  # 写入投影
        dst.GetRasterBand(1).WriteArray(array)
    else:
        # save all bands
        n_band = array.shape[-1]
        dst = driver.Create(path, array.shape[1], array.shape[0], n_band, gdal.GDT_Float32)
        dst.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dst.SetProjection(im_proj)  # 写入投影
        for b in range(n_band):
            dst.GetRasterBand(b + 1).WriteArray(array[:, :, b])
    del dst
    gc.collect()


def trans_int16(input, output):
    image = gdal.Open(input)
    geotransform = image.GetGeoTransform()
    projinfo = image.GetProjection()
    int_ndvi = image.ReadAsArray()
    float_ndvi = int_ndvi * 0.0001
    float_ndvi[float_ndvi <= 0] = np.nan
    float_ndvi[float_ndvi > 1] = np.nan
    writeTiff(int_ndvi, geotransform, projinfo, output)
    del image, geotransform, projinfo, float_ndvi, int_ndvi
    gc.collect()


if __name__ == '__main__':
    input_dir = r".\input dir"  # folder of input images
    output_dir = r".\output dir"  # folder of output images

    path_list = os.listdir(input_dir)
    tif_files = list()
    for filename in path_list:
        if os.path.splitext(filename)[1] == '.tif':
            tif_files.append(filename)

    total = len(tif_files)

    for idx, i in enumerate(tif_files, start=1):
        progress = f"{idx}/{total}"
        tif = input_dir + '\\' + i
        out_tif = output_dir + '\\' + i

        trans_int16(tif, out_tif)

        print('Process：', progress, '|Fin：', i)
        del progress, tif, out_tif
        gc.collect()

    print('Finished! | Total time：', time.time() - a, 's')
