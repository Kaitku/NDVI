import os
from osgeo import gdal
import time
from Functions import extract_by_shp_rasterio, read_shape
import gc


a = time.time()


if __name__ == "__main__":
    input_path = r".\input dir"  # folder of input images
    out_path = r".\output dir"  # folder of output images
    shp_boundary = r".\SHP\Sentinel-2 10m Land UseLand Cover\2022\crops.shp"
    outname = str('-crops')  # outname = False, when no suffix is needed

    path_list = os.listdir(input_path)
    tif_files = list()
    for filename in path_list:
        if os.path.splitext(filename)[1] == '.tif':
            tif_files.append(filename)

    total = len(tif_files)

    for idx, i in enumerate(tif_files, start=1):
        progress = f"{idx}/{total}"
        input = input_path + '\\' + i
        temp = out_path + '\\' + os.path.splitext(i)[0] + "_temp" + os.path.splitext(i)[1]
        if outname:
            out = out_path + '\\' + os.path.splitext(i)[0] + outname + os.path.splitext(i)[1]
        else:
            out = out_path + '\\' + i

        gdal.Warp(temp, input, dstSRS='EPSG:32648', xRes=30, yRes=30, targetAlignedPixels=True)
        extract_by_shp_rasterio(shp_boundary, temp, out)
        text = read_shape(input, out)
        print('Process：', progress, '|Fin：', os.path.split(out)[-1], 'Before&After shape:', text[0], text[1])
        os.remove(temp)

        del input, temp, out, text
        gc.collect()

    print('Finished! | Total time：', time.time() - a, 's')
