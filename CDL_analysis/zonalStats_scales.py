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

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

SRB_3km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
SRB_1km=gpd.read_file('Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')


ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/30m/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()


from rasterio.mask import mask

# extract the geometry in GeoJSON format
geoms = SRB_3km.geometry.values # list of shapely geometries

#LOOP THROUGH THE GEOMETRIES HERE
geometry = geoms[0] # shapely geometry
# transform to GeJSON format
from shapely.geometry import mapping
geoms = [mapping(geoms[0])]

# extract the raster values values within the polygon, The out_image result is a Numpy masked array
with rasterio.open(files[0]) as src:
     out_image, out_transform = mask(src, geoms, crop=True)


# no data values of the original raster
no_data=src.nodata
print no_data
-9999.0
# extract the values of the masked array
data = out_image.data[0]
# extract the row, columns of the valid values
import numpy as np
row, col = np.where(data != no_data) 
elev = np.extract(data != no_data, data)



#calculate Shannon diversity index within each 3km polygon at 1km and 30m scale
with rio.open(files[0]) as src:
     r =src.read(1)
     
     #need to count the number of each landcover in each 3km pixel

     for j in np.arange(28): 
     counts[j]=np.count_nonzero(cdl == j+1) 
  