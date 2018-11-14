#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 17:54:39 2018

@author: kek25
"""

import rasterio as rio
from rasterio.plot import show
from rasterio.mask import mask
from shapely.geometry import mapping
import numpy as np
import os
import matplotlib.pyplot as plt
import geopandas as gpd

os.chdir("D:/Dropbox/BSU/Python/Data/CDL")
#os.chdir("/Users/kek25/Dropbox/BSU/Python/Data/CDL")
files = glob.glob('*.txt')

# open the lidar chm
with rio.open(files[0]) as src:
    cdl = src.read(masked = True)[0]
    extent = rio.plot.plotting_extent(src)
    cdl_profile = src.profile


counties = gpd.read_file('SRB_counties.shp')



fig, ax = plt.subplots(figsize = (10,10))
ax.imshow(cdl, 
          cmap='terrain', 
          extent=extent)
counties.plot(ax=ax, alpha=.6, color='g');



with rio.open(counties) as src:
    extent_geojson = mapping(counties['geometry'][0])
    lidar_chm_crop, crop_affine = mask(src, 
                                   shapes=[extent_geojson], 
                                   crop=True)
    # metadata for writing or exporting the data
    cdl_meta = src.meta.copy()