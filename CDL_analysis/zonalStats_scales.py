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

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_3km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
SRB_1km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')


ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/30m/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

counts= zonal_stats(SRB_3km, files[0], stats=["unique"])

#not working yet
cx=[d.values() for d in counts]

for key, value in cx.items():
    c=value

    


#calculate Shannon diversity index for each year at each scale
#need counts for each shapefile 
l=np.zeros((28,3))
sh=np.zeros((8,3))

for y in np.arange(8):
    x= counts[years[y]]
    for s in np.arange(3):
        temp = []
        dictlist = []
        for key, value in x.items():
            temp = value[s]
            dictlist.append(temp)
        
        l[:,s]=np.asarray(dictlist)

si=sci.alpha.shannon(counts)