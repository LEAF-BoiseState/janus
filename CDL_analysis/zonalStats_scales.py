#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 17:10:15 2019

@author: kek25

calculate zonal stats using polygon coverage
"""

#clip polygon coverage to the county
#calculate shannons diversity at 1km and 3km
#other zonal stats?

import os
import geopandas as gpd
from geopandas import GeoDataFrame
import glob
from rasterstats import zonal_stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from osgeo import gdal
from math import log as ln

#------- IMPORT DATA
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_3km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
SRB_1km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')

ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/30m/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

#------- COPY RASTER for saving output from zonal stats
g30 = gdal.Open(files[0])
g30_meta = g30.meta.copy()
gcam30m = np.array(g30.GetRasterBand(1).ReadAsArray())
gcam30m[gcam30m==0] = np.nan #retains shape

#------- Define shannons diversity index 
def sdi(data):
    """ Given a dictionary { 'species': count } , returns the SDI
    >>> sdi({'a': 10, 'b': 20, 'c': 30,}) 1.01"""   
    def p(n, N):
        """ Relative abundance """
        if n is  0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)        
    N = sum(data.values())
    return -sum(p(n, N) for n in data.values() if n is not 0)

#------- Retreive categorical counts for each pixel
counts = zonal_stats(SRB_3km, files[0], categorical=True, geojson_out=True) # when no geojson_out it's just a list of dictionaries
#------- define CDL keys for subsetting dictionary
crop_keys=np.arange(1,28)
# ------ Calculate and store Shannons Diversity Index

sdix=[]
for n in np.arange(len(counts)):
    countx=counts[n]
    count_prop=countx['properties'] 
    cdls={k:count_prop[k] for k in crop_keys if k in count_prop} #subest data to dictionary of keys: count
    sd=sdi(cdls)
    sdix.append(sd)
    counts[n].update({'sd' : sd})  #calculate Shannons Index append to dictionary
    
SRB_3km['sd']= sdix
SRB_3km.plot(column='sd') #WORKS! need to mask out the nans
