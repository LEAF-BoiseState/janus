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
import geopandas as gp
import rasterio as rio
import glob

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_3km=gp.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
SRB_1km=gp.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')


ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/30m/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

#calculate Shannon diversity index within each 3km polygon at 1km and 30m scale
with rio.open(files[0]) as src:
     r =src.read(1)
     cdl=r[r>0] #flattens the data
     
     #need to count the number of each landcover in each 3km pixel

     for j in np.arange(28): 
     counts[j]=np.count_nonzero(cdl == j+1) 
  