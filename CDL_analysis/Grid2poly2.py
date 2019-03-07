#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 13:50:50 2019

@author: kendrakaiser

Uses raster to create a coverage of polygons for each grid cell
"""
import gdal
import numpy as np

import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon 
from fiona.crs import from_epsg

#=============================================================================#
# Set working  directories and inout files                                    #
#=============================================================================#

GCAM_ReadDir = ''
GCAM_ReadFile_1km = 'gcam_2010_srb_1000_utm11N.tiff'

OutFileName = 'SRB_poly_1km.shp'

src_ds1km = gdal.Open(GCAM_ReadDir+GCAM_ReadFile_1km)
srcband = src_ds1km.GetRasterBand(1)

#=============================================================================#
#Create Polygon from grid                                                     #
#=============================================================================#
src = src_ds1km

srcarray = src.ReadAsArray().astype(np.float)

x_index =np.arange(srcarray.shape[1]) 
y_index = np.arange(srcarray.shape[0])
(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = src.GetGeoTransform()
x_coords = x_index * x_size + upper_left_x + (x_size / 2) #add half the cell size
y_coords = y_index * y_size + upper_left_y + (y_size / 2) #to centre the point
xc, yc = np.meshgrid(x_coords, y_coords)

#create a list of all the polygons in the grid
vert = list()
for i in np.arange(srcarray.shape[1]-1):  
    for j in np.arange(srcarray.shape[0]-1):  
            vert.append([[xc[j, i] , yc[j,i]], [xc[j+1, i], yc[j+1, i]], [xc[j+1, i+1], yc[j+1, i+1]],[xc[j, i+1], yc[j, i+1]]])
 
#create list of polygons
polygons=[Polygon(vert[i]) for i in np.arange(len(vert))]

#convert them to formats for exporting 
polys   = gpd.GeoSeries(MultiPolygon(polygons))
polyagg = gpd.GeoDataFrame(geometry=polys)
polyagg.crs= from_epsg(32611)

#=============================================================================#
#Save Output                                                                  #
#=============================================================================#

polyagg.to_file(filename=OutFileName, driver="ESRI Shapefile")



