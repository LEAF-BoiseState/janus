#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 17:10:15 2019

@author: kek25

calculate zonal stats using polygon coverage
"""
#other zonal stats?

import os
import geopandas as gpd
import glob
from rasterstats import zonal_stats
import numpy as np
from osgeo import gdal
from math import log as ln
from joblib import Parallel, delayed

#=============================================================================#
# Set working  directories and inout files                                    #
#=============================================================================#

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_poly_3km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_clip.shp')
#SRB_poly_1km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_1km_clip.shp')

ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/1km/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

#=============================================================================#
# COPY raster for saving output from zonal stats- is shaefile better??                               
#=============================================================================#
 
g30 = gdal.Open(files[0])
g30_meta = g30.meta.copy()
gcam30m = np.array(g30.GetRasterBand(1).ReadAsArray())
gcam30m[gcam30m==0] = np.nan #retains shape

#=============================================================================#
# Define functions                          
#=============================================================================#
#shannons diversity index    
def sdi(data):
    """ Given a dictionary { 'species': count }, returns sdi"""   
    def p(n, N):
        """ Relative abundance """
        if n is  0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)        
    N = sum(data.values())
    return -sum(p(n, N) for n in data.values() if n is not 0)

# define CDL keys for subsetting dictionary
crop_keys=np.arange(1,28) 

# Retreive categorical counts for each pixel, calculate and store SDI  
def zonalSDI(SRB_poly, file):
    
    counts = zonal_stats(SRB_poly, file, categorical=True, geojson_out=True) # when no geojson_out it's just a list of dictionaries

    sdix=[]
    for n in np.arange(len(counts)):
        countx=counts[n]
        count_prop=countx['properties'] 
        #subest data to dictionary of keys: count
        cdls={k:count_prop[k] for k in crop_keys if k in count_prop} 
        sd=sdi(cdls) #calculate SDI
        sdix.append(sd) #append to vector
     
    varName='sdi_1km_'+ os.path.basename(file)[5:9]
    SRB_poly[varName]= sdix #append to the original polygons- create new name based on filename

#=============================================================================#
# Retreive categorical counts for each pixel, calculate and store SDI                            
#=============================================================================#
Parallel(n_jobs=6, verbose=30, backend='threading')(delayed(zonalSDI)(SRB_poly_3km, files[i]) \
         for i in np.arange(len(files)))

#=============================================================================#
#Save Output                                                                  #
#=============================================================================#
#SRB_poly_1km.plot(column='sdi_30m_2015')

SRB_poly_3km.to_file(filename='SRB_poly_3km_sri', driver="ESRI Shapefile")