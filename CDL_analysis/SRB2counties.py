#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 17:54:39 2018

@author: kek25

Subsets data by county

Future iteration could subset each county in the SRB
"""
import os
import glob
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from rasterio.plot import show
from shapely.geometry import mapping
import numpy as np

os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles')

county = gpd.read_file('Jerome.shp') #-->GeoPandas dataframe
county=county.to_crs(epsg=32611) #reproject bc for some reason not saving the crs from Arc

os.chdir('/Users/kendrakaiser/Documents/Data/GCAM_UTM/30m')
files = glob.glob('*.tiff')

for i in np.arange(8):
    with rio.open(files[i]) as src:
        extent_geojson = mapping(county['geometry'][0])
        county_cdl, affine = mask(src, 
                            [extent_geojson], 
                            crop=True)
        # metadata for writing or exporting the data
        county_meta = src.meta.copy()
        county_meta.update({"height": county_cdl.shape[1],
                         "width": county_cdl.shape[2],
                         "transform": affine})
    
        # Write data
        writeDir='/Users/kendrakaiser/Documents/Data/GCAM_UTM/30m/Jerome/'
        writeFile = files[i].replace('srb','Jerome')
        with rio.open(writeDir+writeFile, 'w', **county_meta) as out:
            out.write(county_cdl)
    
    # Clean up
    src = None
            
show(county_cdl)
