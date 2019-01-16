#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 09:41:43 2019

@author: kendrakaiser
"""
from rasterstats import zonal_stats #zonal stats http://www.perrygeo.com/index2.html, https://pythonhosted.org/rasterstats/manual.html

#create histogram of each year at each scale
#ts plots of each land cover at each scale
#loop through polygon
#use 1km polygon to get histograms of 30m data --> how to summarize this though?


#sample code http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#polygonize-a-raster-band
# https://rasterio.readthedocs.io/en/latest/
# https://pythonhosted.org/rasterstats/manual.html

ReadDir='~/Documents/GitRepos/IM3-BoiseState/CDL_analysis/'
shpFile='SRB_poly_3km.shp'
#=============================================================================#
#Calculate Raster Stats                                                       #
#=============================================================================#

zonal_satats(shp, tif, categorical=TRUE)
