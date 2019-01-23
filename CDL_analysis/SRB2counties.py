#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 17:54:39 2018

@author: kek25
"""
import os
import glob

import rasterio as rio
from rasterio.mask import mask
from shapely.geometry import mapping
import matplotlib.pyplot as plt
import geopandas as gpd


import numpy as np
from rasterio.plot import show


os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles')

Ada = gpd.read_file('Ada.shp')

os.chdir('/Users/kendrakaiser/Documents/Data/GCAM_UTM/1km')
files = glob.glob('*.tiff')

# open data
with rio.open(files[0]) as src:
    cdl = src.read(masked = True)[0]
    extent = rio.plot.plotting_extent(src)
    cdl_profile = src.profile





fig, ax = plt.subplots(figsize = (10,10))
ax.imshow(cdl, 
          cmap='terrain', 
          extent=extent)
Ada.plot(ax=ax, alpha=.6, color='g');



with rio.open(Ada) as src:
    extent_geojson = mapping(Ada['geometry'][0])
    lidar_chm_crop, crop_affine = mask(src, 
                                   shapes=[extent_geojson], 
                                   crop=True)
    # metadata for writing or exporting the data
    cdl_meta = src.meta.copy()