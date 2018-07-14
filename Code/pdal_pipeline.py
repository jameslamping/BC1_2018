"""
Team members: James  Lamping, Nicole Abib, Labeeb Ahmed & Stephen Escarzaga

Description: asdf
"""

# PDAL pipelines:
merge_pipeline = """ {"pipeline":["C:/Users/CBPStaff/Neon_Data/capstone/NEON_D17_TEAK_DP1_319000_4092000_classified_point_cloud.las",
                                  "C:/Users/CBPStaff/Neon_Data/capstone/NEON_D17_TEAK_DP1_320000_4092000_classified_point_cloud.las",
                                  {"type":"filters.merge"},
                                  "C:/Users/CBPStaff/Neon_Data/capstone/test_results/BC1_crop_17_merge.las"]} """

crop_pipeline = """ {"pipeline": ["C:/Users/CBPStaff/Neon_Data/capstone/test_results/BC1_crop_17_merge.las",                       
                                    {"type":"filters.crop",
                                    "bounds":"([319842,320036],[4092064,4092238])"},
                                    "C:/Users/CBPStaff/Neon_Data/capstone/test_results/BC1_crop_17_crop.las"]} """

dtm_pipeline = """ {"pipeline":["C:/Users/CBPStaff/Neon_Data/capstone/test_results/BC1_crop_17_crop.las",
                                {"type":"filters.reprojection",
                                "out_srs":"EPSG:32611"},
                                {"type":"filters.range",
                                 "limits":"Classification[2:2]"},
                                {"gdaldriver":"GTiff",
                                 "output_type":"mean",
                                 "resolution":"1.0",
                                 "data_type":"float",
                                 "type": "writers.gdal",
                                 "radius": 0.5,
                                 "filename":"C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM.tif"}]} """

dsm_pipeline = """ {"pipeline":["C:/Users/CBPStaff/Neon_Data/capstone/test_results/BC1_crop_17_merge.las",
                                {"type":"writers.gdal",
                                "dimension":"Elevation",
                                "data_type":"float",
                                "output_type":"max",
                                "resolution":1.0,
                                "radius": 0.5,
                                "filename":"C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DSM.tif"}]} """

###---- Main script starts here:

import gdal
from gdalconst import *
import numpy as np
import rasterio
import shutil
import pdal
import time

# some functions
def pdal_pipeline(json_file):
    st = time.time()
    """ executes pdal pipeline code """
    pipeline = pdal.Pipeline(json_file)
    pipeline.validate()
    pipeline.execute()
    print("Execution time: {} minutes".format((time.time()-st)/60.0))


"""
###---- Execute functions

pdal_pipeline(merge_pipeline) # 1 merge pipeline
pdal_pipeline(crop_pipeline) # 2 crop pipeline
"""
pdal_pipeline(dtm_pipeline) # 3 dtm pipeline

in_ras = "C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM.tif"
output = "C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM_output_gdal.tif"

# fill gaps in dtm:
raw_dtm = gdal.Open(in_ras, GA_Update)
raw_dtm_band = raw_dtm.GetRasterBand(1)
result = gdal.FillNodata(targetBand = raw_dtm_band, maskBand = None,
                            maxSearchDist = 3, smoothingIterations = 0)
type(result)
# dtm_array = raw_dtm.ReadAsArray()

# dtm_mask = np.where(dtm_array == profile['nodata'], 1, -9999.0).astype('float32')
# dtm_mask(output, 1)

######
# open dataset
# dtm_raw = gdal.Open("D:/test_results/NEON_TEAK_DTM.tif")

# create mask out of null values with DSM models
# in_ras = "C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM.tif"
# with rasterio.open(in_ras) as f:
#     ras = f.read() # read raster

#     mask = np.where(ras => 0, np.nan, 1)

# raw_dtm = rasterio.open(in_ras) # read raster
# mask = np.where(raw_dtm => 0, np.nan, 1) # create mask


# tmp = shutil.copy("C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM.tif", 
#                   "C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM_mask.tif")

# tmp_meta = (rasterio.open(tmp, 'r')).meta # get metadata
# print(tmp_meta['width'], tmp_meta['height'])

# src = rasterio.open(tmp, mode="w", **kwargs)
# print(src)
# # mask = np.where(raster == raster.nodata, 1, -9999)

# # with rasterio.open(tmp, 'w', **tmp_meta) as raster:
# #     # src = rasterio.open(tmp, mode="r+"); print(type(src))
# #     print(raster)
# #     mask = np.where(raster == raster.nodata, 1, -9999)
# #     raster.write(mask)

'''
in_ras = "C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM.tif"
output = "C:/Users/CBPStaff/Neon_Data/capstone/test_results/NEON_TEAK_DTM_output.tif"

with rasterio.open(in_ras) as src:
    array = src.read()
    profile = src.profile
    type(array)

mask = np.where(array == profile['nodata'], 1, -9999.0).astype('float32')

with rasterio.open(output, 'w', **profile) as dst:
    dst.write(mask)
'''