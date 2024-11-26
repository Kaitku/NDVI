import gc
import os
import numpy as np
from osgeo import gdal
from Functions import extract_by_shp_rasterio, writeTiff
import time


a = time.time()


def mosaic(input_a, input_b, output):
    input_array_a = gdal.Open(input_a).ReadAsArray()
    input_array_b = gdal.Open(input_b).ReadAsArray()
    geotransform = gdal.Open(input_a).GetGeoTransform()
    projinfo = gdal.Open(input_a).GetProjection()

    input_array_a[input_array_a <= 0] = np.nan
    input_array_b[input_array_b <= 0] = np.nan
    arr1 = np.nan_to_num(input_array_a, nan=-999)
    arr2 = np.nan_to_num(input_array_b, nan=-999)

    output_array = np.maximum(arr1, arr2)
    output_array[output_array == -999] = np.nan
    writeTiff(output_array, geotransform, projinfo, output)

    del input_array_a, input_array_b, geotransform, projinfo, output_array, arr1, arr2
    gc.collect()


if __name__ == '__main__':
    input_dir_a = r".\input dir 131"  # input folder of Path131 images
    input_dir_b = r".\input dir 132"  # input folder of Path132 images
    out_dir = r".\output dir"  # folder of output images
    shp_boundary = r".\SHP\Sentinel-2 10m Land UseLand Cover\2022\crops.shp"

    for i in range(1, 366):  # DOY for images to mosaic
        input_path_a = input_dir_a + "\VSDF-2022_DOY" + f"{i:03}" + "-131-NDVI.tif"
        input_path_b = input_dir_b + "\VSDF-2022_DOY" + f"{i:03}" + "-132-NDVI.tif"
        out_path_temp = out_dir + "/NDVI-2022_DOY" + f"{i:03}" + "_temp.tif"
        out_path = out_dir + "/NDVI-2022_DOY" + f"{i:03}" + ".tif"

        if os.path.isfile(input_path_a) & os.path.isfile(input_path_b):
            mosaic(input_path_a, input_path_b, out_path_temp)
            extract_by_shp_rasterio(shp_boundary, out_path_temp, out_path)
            os.remove(out_path_temp)
            print('Index：', i, '|FINISH: ', out_path)

            del input_path_a, input_path_b, out_path_temp, out_path
            gc.collect()
        else:
            print(i, "not exists!")
            i += 1

    print('Finished! | Total time：', time.time() - a, 's')
