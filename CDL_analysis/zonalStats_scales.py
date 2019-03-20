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
import skbio.diversity as sci #not working on desktop...
import geopandas as gpd
import glob
from rasterstats import zonal_stats
import numpy as np
import rasterio
import rasterio.mask
import matplotlib.pyplot as plt
import fiona
from osgeo import gdal

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_3km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
SRB_1km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')


ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/30m/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

g30 = gdal.Open(files[0])
g30_meta = g30.meta.copy()
gcam30m = np.array(g30.GetRasterBand(1).ReadAsArray())
gcam30m[gcam30m==0] = np.nan #retains shape

#gcam30m= gcam30m[~np.isnan(gcam30m)]#turns its into one long list


with fiona.open('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp') as shapefile:
    features = [feature["geometry"] for feature in shapefile]
    
with rasterio.open(files[0]) as src:
    out_image, out_transform = rasterio.mask.mask(src, features, crop=True)
    out_meta = src.meta.copy()

from math import log as ln
def sdi(data):
    """ Given a hash { 'species': count } , returns the SDI
    >>> sdi({'a': 10, 'b': 20, 'c': 30,}) 1.0114042647073518"""
   # need to create a dictionary that results in ID : number of counts for each raster subset
    #{i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)}
    
    def p(n, N):
        """ Relative abundance """
        if n is  0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)
            
    N = sum(data.values())
    
    return -sum(p(n, N) for n in data.values() if n is not 0)
    

counts= zonal_stats(SRB_3km, files[0], stats=['count'],  
                    geojson_out=True) #add_stats={'shannon': sdi}


#turn into list
cx=np.hstack([list(d.values()) for d in counts])

#REMOVES IMPT STUFF
cf=np.asarray([x for x in cx if x is not None])
#calculate Shannon diversity index for each year at each scale
#needs a vector of counts of each lc type for each shapefile 
si=np.zeros((cf.size))

for i in np.arange(25512):
    c=cf[i]
    si[i]=sci.alpha.shannon(c)

