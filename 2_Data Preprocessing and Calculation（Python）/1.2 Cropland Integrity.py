import numpy as np
import time
import os
import gc
import pandas as pd
from Functions import read_img

a = time.time()


def cropland_count(path_count, path_basic, value, band_nums):
    arr_0 = read_img(path_count)
    arr_1 = read_img(path_basic)
    if arr_0 is None or arr_1 is None:
        return None, None
    count = int(np.sum(arr_0 > value) / band_nums)
    crops = int(np.sum(arr_1 > value))
    max_value = np.nanmax(arr_0)
    del arr_0, arr_1
    gc.collect()
    return count / crops, max_value


if __name__ == "__main__":
    input_path = r".\input dir"  # folder of input images
    basic_path = r".\basic\2022_crops_noncube.tif"  # path of the basic cropland tif
    output_excel = r".\Cropland Integrity.xlsx"  # path of output summarized excel
    count = []

    # 获取 .tif 文件列表
    path_list = os.listdir(input_path)
    tif_files = [f for f in path_list if f.endswith(".tif")]

    total = len(tif_files)

    processed_files = []

    for idx, i in enumerate(tif_files, start=1):
        progress = f"{idx}/{total}"
        input_file = os.path.join(input_path, i)
        rate, max_value = cropland_count(input_file, basic_path, 0, 1)
        if rate is None:  # fail file
            print(f"Skipping file {i} due to processing error.")
            continue
        count.append([rate])
        processed_files.append(i)
        print(f"Process：{progress} | Cropland Integrity（%）：{rate * 100:.2f}, Maximum：{max_value:.2f}")

        del input_file, rate
        gc.collect()

    # save results to excel
    data_df = pd.DataFrame(count, columns=["RATE"])
    data_df.index = processed_files
    writer = pd.ExcelWriter(output_excel)
    data_df.to_excel(writer, "page_1", float_format="%.8f")
    writer.close()

    print('Finished! | Total time：', time.time() - a, 's')
