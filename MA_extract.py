import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

#####################################################################################
# import additional packages
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import os
import glob
import random as rd
import shapely
import struct
from Tools import return_raster_values


#####################################################################################
root_folder = "\\\\141.20.140.91\SAN_Projects\Spring\workspace\Katja\germany"
data_path = "\\\\141.20.140.222\Dagobah\edc\level2"
os.chdir("\\\\141.20.140.91\SAN_Projects\Spring\workspace\Katja\germany/")

# open shapefiles: tiles and stations
sample_shp = shp_driver.Open(root_folder + '.shp', 1)
sample = sample_shp.GetLayer()
tiles_shp = shp_driver.Open(root_folder + "/germany.shp", 1)
tiles = tiles_shp.GetLayer()

# get all tile directories
tile_list =  []
tile_feat = tiles.GetNextFeature()
while tile_feat:
    name = tile_feat.GetField('Name')
    direct = os.path.join(data_path, name)
    tile_list.append(direct)
    tile_feat = tiles.GetNextFeature()
print(tile_list)
tiles.ResetReading()

date_list = list(range(20160815, 20180815))
date_list = [str(item) for item in date_list]

endlist = ['QAI', 'BOA']

# check tile of coordinate:
# tile_feat2 = tiles.GetNextFeature()
# while tile_feat2:
#     t_id = tile_feat2.GetField('Name')
#     geom_t = tile_feat2.GetGeometryRef()
#     if geom_t.Contains(rd_point):
#         file_list = []
#         for path in tile_list:
#             if t_id in path:
#                 for root, dirs, files in os.walk(path):
#                     for name in files:
#                         if any(end in name for end in endlist):
#                             if name.endswith(('.tif')):
#                                 if any(date in name for date in date_list):
#                                     file_list.append(os.path.join(root, name))
#     tile_feat2 = tiles.GetNextFeature()
# tiles.ResetReading()
# print('files:', len(file_list))
# # data_list = return_raster_values(x_s, y_s, file_list)
# # print(data_list)
# # final_sample.append(data_list)



#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")