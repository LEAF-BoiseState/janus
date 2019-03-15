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
import rasterio as rio
import glob
from rasterstats import zonal_stats
import rasterstats as rs
import pandas as pd
from rasterio.plot import show

from rasterio.mask import mask
from shapely.geometry import mapping

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_3km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
SRB_1km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')


ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/30m/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

# extract the geometry in GeoJSON format
geoms = SRB_3km.geometry.values # list of shapely geometries
#LOOP THROUGH THE GEOMETRIES HERE
geometry = geoms[5000] # shapely geometry
# transform to GeJSON format
geom = [mapping(geoms[0])]

# extract the raster values values within the polygon, The out_image result is a Numpy masked array
with rio.open(files[0]) as src:
    #cdl = src.read(1, masked =True) #numpy array
    #cdl_meta = src.profile
    out_image, out_transform = mask(src, geom, crop=True)

    #cdl[cdl == 0] = np.nan


# no data values of the original raster
no_data=src.nodata

# extract the values of the masked array
data = out_image.data[0]
# extract the row, columns of the valid values
import numpy as np
row, col = np.where(data != no_data) 
val = np.extract(data != no_data, data)
from rasterio import Affine # or from affine import Affine
T1 = out_transform * Affine.translation(0.5, 0.5) # reference the pixel centre
rc2xy = lambda r, c: (c, r) * T1 

d = gpd.GeoDataFrame({'col':col,'row':row,'val':val})
# coordinate transformation
d['x'] = d.apply(lambda row: rc2xy(row.row,row.col)[0], axis=1)
d['y'] = d.apply(lambda row: rc2xy(row.row,row.col)[1], axis=1)
# geometry
from shapely.geometry import Point
d['geometry'] =d.apply(lambda row: Point(row['x'], row['y']), axis=1)
# first 2 points
d.head(2)

  