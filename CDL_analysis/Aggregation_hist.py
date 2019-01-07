#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 13:50:50 2019

@author: kendrakaiser
"""
import gdal
import ogr
import matplotlib.pyplot as plt
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

#creates vector polygons for all connected regions of pixels in the raster sharing a common pixel value- not quite what we need
tst= gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None )

tst= np.float64(srcband.ReadAsArray())
#sf = shapefile.Reader("SRB_counties")
plt.imshow(tst)
plt.grid(True)

