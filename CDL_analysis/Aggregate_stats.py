#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 09:41:43 2019

@author: kendrakaiser
"""
from rasterstats import zonal_stats #zonal stats http://www.perrygeo.com/index2.html, https://pythonhosted.org/rasterstats/manual.html

#looping through polygon
#cal histogram for one polygon
#histogram from polygon (zonal/focal histogram)

#sample code http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#polygonize-a-raster-band


ReadDir='~/Documents/GitRepos/IM3-BoiseState/CDL_analysis/'
shpFile='SRB_poly_3km.shp'
#=============================================================================#
#Calculate Raster Stats                                                       #
#=============================================================================#

zonal_satats(shp, tif, categorical=TRUE)
