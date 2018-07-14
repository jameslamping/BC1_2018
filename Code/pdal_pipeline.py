"""
Team members: James  Lamping, Nicole Abib, Labeeb Ahmed & Stephen Escarzaga

Description: asdf
"""



###---- Main script starts here:

import glob
import gdal
from gdalconst import *
import numpy as np
import rasterio
import shutil
import pdal
import time

###--- Main dir:
main_dir = "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/{}/*.las"  
las_2017, las_2018 =  glob.glob(main_dir.format(2017)), glob.glob(main_dir.format(2018))

# PDAL pipelines:
merge_pipeline_2017 = """ {"pipeline":["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/NEON_D17_TEAK_DP1_319000_4092000_classified_point_cloud_2017.las", 
                                        "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/NEON_D17_TEAK_DP1_320000_4092000_classified_point_cloud_2017.las",
                                        {"type":"filters.merge"},
                                        "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/BC1_merge_2017.las"]} """

merge_pipeline_2018 = """ {"pipeline":["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/NEON_D17_TEAK_DP1_319000_4092000_classified_point_cloud_2018.las", 
                                        "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/NEON_D17_TEAK_DP1_320000_4092000_classified_point_cloud_2018.las",
                                        {"type":"filters.merge"},
                                        "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/BC1_merge_2018.las"]} """


crop_pipeline_2017 = """ {"pipeline": ["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/BC1_merge_2017.las",                       
                                    {"type":"filters.crop",
                                    "bounds":"([319842,320036],[4092064,4092238])"},
                                    "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/BC1_crop_2017.las"]} """

crop_pipeline_2018 = """ {"pipeline": ["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/BC1_merge_2018.las",                       
                                    {"type":"filters.crop",
                                    "bounds":"([319842,320036],[4092064,4092238])"},
                                    "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/BC1_crop_2018.las"]} """

dtm_pipeline_2017 = """ {"pipeline":["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/BC1_crop_2017.las",
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
                                 "filename":"C:/Users/CBPStaff/GitHub/BC1_2018_data/raster/NEON_TEAK_DTM_2017.tif"}]} """

dtm_pipeline_2018 = """ {"pipeline":["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/BC1_crop_2018.las",
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
                                 "filename":"C:/Users/CBPStaff/GitHub/BC1_2018_data/raster/NEON_TEAK_DTM_2018.tif"}]} """

dsm_pipeline_2017 = """ {"pipeline":["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2017/BC1_crop_2017.las",
                            {"type":"writers.gdal",
                            "dimension":"Z",
                            "data_type":"float",
                            "output_type":"max",
                            "resolution":1.0,
                            "radius": 0.5,
                            "filename":"C:/Users/CBPStaff/GitHub/BC1_2018_data/raster/NEON_TEAK_DSM_2017.tif"}]} """

dsm_pipeline_2018 = """ {"pipeline":["C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/2018/BC1_crop_2018.las",
                            {"type":"writers.gdal",
                            "dimension":"Z",
                            "data_type":"float",
                            "output_type":"max",
                            "resolution":1.0,
                            "radius": 0.5,
                            "filename":"C:/Users/CBPStaff/GitHub/BC1_2018_data/raster/NEON_TEAK_DSM_2018.tif"}]} """
# some functions
def pdal_pipeline(json_file):
    st = time.time()
    """ executes pdal pipeline code """
    print(json_file)
    pipeline = pdal.Pipeline(json_file)
    pipeline.validate()
    pipeline.execute()
    print("Execution time: {} minutes".format((time.time()-st)/60.0))

skip_pipeline = 1 # toggle on/off
pipelines_2017 = [merge_pipeline_2017, crop_pipeline_2017, dtm_pipeline_2017, dsm_pipeline_2017]
pipelines_2018 = [merge_pipeline_2018, crop_pipeline_2018, dtm_pipeline_2018, dsm_pipeline_2018]

###---- Execute PDAL pipeline functions
if skip_pipeline == 1:
    for year in [pipelines_2017, pipelines_2018]:
        for json in year:
            pdal_pipeline(json)
else:
    pass

###---- Execute fill gaps functions
raster_dir = "C:/Users/CBPStaff/GitHub/BC1_2018_data/raster/{}.tif"
output_dir = "C:/Users/CBPStaff/GitHub/BC1_2018_data/output/{}.tif"

def fill_gaps(raster_dir, output_dir, in_file, out_file, window):
    print ('Filling gaps...')
    # fill gaps in dtm:
    in_file = raster_dir.format(in_file)
    out_file = output_dir.format(out_file)

    copy_orig_ras = shutil.copy(in_file, out_file)

    temp_file = gdal.Open(copy_orig_ras, GA_Update) #read input file
    temp_band = temp_file.GetRasterBand(1) # get band 1

    temp_filled = gdal.FillNodata(targetBand = temp_band, maskBand = None,
                                    maxSearchDist = int(window), smoothingIterations = 0)

    original_ras = gdal.Open(in_file, GA_ReadOnly)
    temp_filled = np.where(original_ras == -9999.0, temp_filled, original_ras)

    temp_filled = None
    
    print ('...gaps filled!')

# input_file, output_file, MaxDistance
dsm_dict = {2017: ('NEON_TEAK_DSM_2017', 'NEON_TEAK_DSM_2017_final', 3),
            2018: ('NEON_TEAK_DSM_2018', 'NEON_TEAK_DSM_2018_final', 3)}

dtm_dict = {2017: ('NEON_TEAK_DTM_2017', 'NEON_TEAK_DTM_2017_final', 4),
            2018: ('NEON_TEAK_DTM_2018', 'NEON_TEAK_DTM_2018_final', 4)}

for k,v in dsm_dict.items():
    in_file = v[0]
    out_file = v[1]
    window = v[2]
    print(in_file, out_file, window)
    fill_gaps(raster_dir, output_dir, in_file, out_file, window)

for k,v in dtm_dict.items():
    in_file = v[0]
    out_file = v[1]
    window = v[2]
    fill_gaps(raster_dir, output_dir, in_file, out_file, window)

"""BEWARE OF MONSTERS BELOW"""
##################################################################
# dtm_array = raw_dtm.ReadAsArray()

# dtm_mask = np.where(dtm_array == profile['nodata'], 1, -9999.0).astype('float32')
# dtm_mask(output, 1)

######
# open dataset
# dtm_raw = gdal.Open("D:/test_results/NEON_TEAK_DTM.tif")

# create mask out of null values with DSM models
# in_ras = "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/NEON_TEAK_DTM.tif"
# with rasterio.open(in_ras) as f:
#     ras = f.read() # read raster

#     mask = np.where(ras => 0, np.nan, 1)

# raw_dtm = rasterio.open(in_ras) # read raster
# mask = np.where(raw_dtm => 0, np.nan, 1) # create mask


# tmp = shutil.copy("C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/NEON_TEAK_DTM.tif", 
#                   "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/NEON_TEAK_DTM_mask.tif")

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


# in_ras = "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/NEON_TEAK_DTM.tif"
# output = "C:/Users/CBPStaff/GitHub/BC1_2018_data/LiDAR/NEON_TEAK_DTM_output.tif"

# with rasterio.open(in_ras) as src:
#     array = src.read()
#     profile = src.profile
#     type(array)

# mask = np.where(array == profile['nodata'], 1, -9999.0).astype('float32')

# with rasterio.open(output, 'w', **profile) as dst:
#     dst.write(mask)
