from osgeo import gdal
import numpy as np
from Functions import read_img, writeTiff, read_shape
import time
import os
import gc


a = time.time()


def add(path, out_path, value):
    dataset = gdal.Open(path)
    geotransform = dataset.GetGeoTransform()
    projinfo = dataset.GetProjection()

    # read image to array
    arr_0 = read_img(path)[:, :, :]
    row_0 = int(arr_0.shape[0])
    col_0 = int(arr_0.shape[1])
    bands = int(arr_0.shape[-1])
    array_0 = np.where(np.isnan(arr_0), value, arr_0)
    array = np.where(array_0 < 0, value, array_0)

    # cubic
    col_2 = int(15-col_0)
    arr_0_1 = np.full((row_0, col_2, bands), value)
    arr = np.append(array, arr_0_1, axis=1)
    row = int(arr.shape[0])
    col = int(arr.shape[1])
    row_2 = int(col - row)
    arr_0_2 = np.full((row_2, col, bands), value)
    arr_1 = np.append(arr, arr_0_2, axis=0)

    writeTiff(arr_1, geotransform, projinfo, out_path)
    del dataset, geotransform, projinfo, arr_0, row_0, col_0, bands, array_0, array, col_2, arr_0_1, arr, row, col, row_2, arr_0_2, arr_1
    gc.collect()


if __name__ == '__main__':
    input_path = r".\input dir"  # folder of input images
    out_path = r".\output dir"  # folder of output images
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
        if outname:
            out = out_path + '\\' + os.path.splitext(i)[0] + outname + os.path.splitext(i)[1]
        else:
            out = out_path + '\\' + i

        add(input, out, 0)
        text = read_shape(input, out)
        print('Process：', progress, '|Fin：', os.path.split(out)[-1], 'Before&After shape:', text[0], text[1])

        del input, out, text
        gc.collect()

    print('Finished! | Total time：', time.time() - a, 's')
