#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 13:50:50 2019

@author: kendrakaiser
"""
import gdal
import ogr
from matplotlib import pyplot as plt
import shapefile
import numpy as np
import rasterio
from rasterstats import zonal_stats #zonal stats http://www.perrygeo.com/index2.html, https://pythonhosted.org/rasterstats/manual.html
#


#target grid
#polygon coverrgae grid->poly
#looping through polygon
#cal histogram for one polygon
#histogram from polygon (zonal/focal histogram)

#sample code http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#polygonize-a-raster-band

#=============================================================================#
# Set working  directories                                                    #
#=============================================================================#

GCAM_ReadDir = '/Users/kendrakaiser/Documents/Data/GCAM_UTM'
GCAM_ReadFile_1km = '/1km/gcam_2010_srb_1000_utm11N.tiff'

GCAM_ReadFile_3km = '/3km/gcam_2010_srb_utm11N_3000_utm11N.tiff'
src_ds3km = gdal.Open(GCAM_ReadDir+GCAM_ReadFile_3km)

src_ds1km = gdal.Open(GCAM_ReadDir+GCAM_ReadFile_1km)
srcband = src_ds1km.GetRasterBand(1)

#=============================================================================#
#Create Polygon from grid                                                     #
#=============================================================================#

dst_layername = "SRB_polygon_1km"
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
dst_layer = dst_ds.CreateLayer(dst_layername, srs = 'EPSG:32611' )

#alternative method
import geopandas as gpd
from shapely import geometry
from shapely.geometry import Polygon, MultiPolygon, asShape
from shapely.ops import unary_union, cascaded_union

a=srcband.ReadAsArray().astype(np.float)
x_index =np.arange(763) 
y_index = np.arange(484)
(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = src_ds1km.GetGeoTransform()
x_coords = x_index * x_size + upper_left_x + (x_size / 2) #add half the cell size
y_coords = y_index * y_size + upper_left_y + (y_size / 2) #to centre the point
xc, yc = np.meshgrid(x_coords, y_coords)

#create a list of all the polygons in the grid
vert = list()
for i in np.arange(762):  
    for j in np.arange(483):  
            vert.append([[xc[j, i] , yc[j,i]], [xc[j+1, i], yc[j+1, i]], [xc[j+1, i+1], yc[j+1, i+1]],[xc[j, i+1], yc[j, i+1]]])
 
for i in np.arange(6):
    polygons[i] = Polygon(vert[i])
    
 5+5   
polygons=[Polygon(vert[i]) for i in np.arange(len(vert))]
polys  = MultiPolygon(polygons)

# get the union of the polygons
joined = unary_union(polygons)
         
vertpoly=geometry.Polygon(vert)
crs = {'init': 'EPSG:32611'}
poly1km = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[vertpoly]) 
poly1km.plot(edgecolor='black')


poly1km.to_file(filename='SRB_poly_1km.shp', driver="ESRI Shapefile")





#=============================================================================#
#Calculate Raster Stats                                                       #
#=============================================================================#

zonal_satats(shp, tif, categorical=TRUE)
