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
from random import randint
import shapely
import struct
from Tools import return_raster_values

#####################################################################################
root_folder = "\\\\141.20.140.91\SAN_Projects\Spring\workspace\Katja\germany"
data_path = "\\\\141.20.140.222\Dagobah\edc\level2"
save_folder = "\\\\141.20.140.91\SAN_Projects\Spring\workspace\Katja\germany\sample_split/"
os.chdir("\\\\141.20.140.91\SAN_Projects\Spring\workspace\Katja\germany")

# get driver
mem_driver = ogr.GetDriverByName('Memory')
shp_driver = ogr.GetDriverByName("ESRI Shapefile")

undist_forest = gdal.Open(root_folder + "/germany_landcover_2015_g1416lc3_dbf_undisturbed_erode3x3_mmu11.bsq")
gt_for = undist_forest.GetGeoTransform()

# open shapes
station_shp = shp_driver.Open(root_folder + '/dwd/stat_dwd_5km_300px.shp', 1)
station = station_shp.GetLayer()
tiles_shp = shp_driver.Open(root_folder + "/germany.shp", 1)
tiles = tiles_shp.GetLayer()

# corner coordinates of forest raster
x_min, y_max = gt_for[0], gt_for[3]
x_max = x_min + gt_for[1] * undist_forest.RasterXSize
y_min = y_max + gt_for[5] * undist_forest.RasterYSize

# setup shapefile for samples
data_source_s = shp_driver.CreateDataSource('samples.shp')
srs_s = osr.SpatialReference()
srs_s.ImportFromEPSG(3035)
layer_s = data_source_s.CreateLayer("samples", srs_s, ogr.wkbPoint)
field0 = ogr.FieldDefn("ID", ogr.OFTInteger)
field1 = ogr.FieldDefn('ID_s', ogr.OFTInteger)
field2 = ogr.FieldDefn('ID_sp', ogr.OFTInteger)
layer_s.CreateField(field0)
layer_s.CreateField(field1)
layer_s.CreateField(field2)
defn_s = layer_s.GetLayerDefn()


# create buffer shapefile in Memory
data_source = mem_driver.CreateDataSource('temp.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(3035)
layer = data_source.CreateLayer("temp", srs, ogr.wkbPolygon)
defn = layer.GetLayerDefn()
bufferDist = 5000
for feature in station:
    field = ogr.FieldDefn('ID', ogr.OFTInteger)
    layer.CreateField(field)
    ingeom = feature.GetGeometryRef()
    geomBuffer = ingeom.Buffer(bufferDist)
    outFeature = ogr.Feature(defn)
    outFeature.SetGeometry(geomBuffer)
    ID = feature.GetField('Stations_i')
    outFeature.SetField('ID', ID)
    layer.CreateFeature(outFeature)
station.ResetReading()

min_dist = 30
sample_list = []
final_sample = []
b_feat = layer.GetNextFeature()
x_sample = []
y_sample = []
nr = 0
split_c = 0
while b_feat:
    samples = []
    geom_b = b_feat.GetGeometryRef()
    x_min_b, x_max_b, y_min_b, y_max_b = b_feat.geometry().GetEnvelope()  # get extent of buffer
    ID = b_feat.GetField('ID')
    print(ID)
    nr += 1
    c = 0
    print(nr)
    while len(samples) < 30:
        x_s = rd.uniform(x_min_b, x_max_b)
        y_s = rd.uniform(y_min_b, y_max_b)
        rd_point = ogr.Geometry(ogr.wkbPoint)
        rd_point.AddPoint(x_s, y_s)
        if geom_b.Contains(rd_point):  # if point within buffer
            if x_s > x_min and x_s < x_max and y_s > y_min and y_s < y_max:  # if within raster image boundaries
                if all(abs(x - x_s) > min_dist for x in x_sample) == True or all(
                        abs(y - y_s) > min_dist for y in y_sample) == True:
                    px_ras = int(
                        (x_s - gt_for[0]) / gt_for[1])  # calculate absolute raster coordinates for disturbance raster
                    py_ras = int((y_s - gt_for[3]) / gt_for[5])
                    # check if sample within undisturbed forest:
                    forest = undist_forest.GetRasterBand(1)
                    struc_for = forest.ReadRaster(px_ras, py_ras, 1, 1)
                    if struc_for is None:
                        val_for = struc_for
                    else:
                        val_for = struct.unpack('b', struc_for)
                        val_for = val_for[0]
                        if val_for == 1:
                            new_file_list = []
                            c += 1
                            sample_list.append([ID, c, x_s, y_s])
                            x_sample.append(x_s)
                            y_sample.append(y_s)
                            samples.append(1)
                            # shapefile:
                            pt = ogr.Geometry(ogr.wkbPoint)
                            pt.AddPoint(x_s, y_s)
                            feat = ogr.Feature(defn_s)
                            feat.SetGeometry(pt)
                            feat.SetField('ID', ID)
                            feat.SetField('ID_s', c)
                            split_c += 1
                            if split_c <= 16:
                                feat.SetField('ID_sp', split_c)
                            else:
                                feat.SetField('ID_sp', 1)
                                split_c = 1
                            layer_s.CreateFeature(feat)
                            print('sample:', c)
                    feat = None
    b_feat = layer.GetNextFeature()
layer.ResetReading()

np.savetxt("samples.csv", sample_list, delimiter=",", fmt='%s')


# split samples in 8 parts
#
# for i in list(range(1,17)):
#     inds = ogr.Open('samples.shp')
#     inlyr=inds.GetLayer()
#     inlyr.SetAttributeFilter("ID_sp = '"+ str(i) + "'")
#     drv = ogr.GetDriverByName( 'ESRI Shapefile' )
#     outds = drv.CreateDataSource(save_folder + "sample_"+ str(i) +".shp" )
#     outlyr = outds.CopyLayer(inlyr,"sample_"+ str(i))
#     del inlyr,inds,outlyr,outds
# print("done")
#


#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")
