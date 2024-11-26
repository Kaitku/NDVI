import gc
import os
import numpy as np
from osgeo import gdal
import fiona
import rasterio
from rasterio.mask import mask


def read_img(path):
    try:
        naip_ds = gdal.Open(path)
        nbands = naip_ds.RasterCount
        band_data = []
        for b in range(nbands):
            band_data.append(naip_ds.GetRasterBand(b + 1).ReadAsArray())
        img = np.dstack(band_data)
        return img.astype("float")
    except Exception:
        return None


def extract_by_shp_rasterio(in_shp_path, in_raster_path, out_raster_path):
    with fiona.open(in_shp_path, "r", encoding='utf-8') as shapefile:
        # 获取所有要素feature的形状geometry
        geoms = [feature["geometry"] for feature in shapefile]

    # 裁剪
    with rasterio.open(in_raster_path) as src:
        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()


    # 更新输出文件的元数据
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    # 保存
    with rasterio.open(out_raster_path, "w", **out_meta) as dest:
        dest.write(out_image)


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


def read_shape(before, after):
    dataset = gdal.Open(before)
    dataset_2 = gdal.Open(after)
    text = list()
    text.append([dataset.RasterXSize, dataset.RasterYSize])
    text.append([dataset_2.RasterXSize, dataset_2.RasterYSize])
    return text


def masktif(origin, ndvi, index, bkg):
    basic = gdal.Open(origin).ReadAsArray()
    mask = np.array(basic == index)
    crops = np.where(mask, ndvi, bkg)
    del mask, basic
    gc.collect()
    return crops

