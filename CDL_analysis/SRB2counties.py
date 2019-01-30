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
import matplotlib.pyplot as plt

os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles')

county = gpd.read_file('Ada.shp') #-->GeoPandas dataframe
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


import earthpy as et
os.chdir(os.path.join(et.io.HOME, 'earth-analytics'))
# Import clip_data.py as a module so you can access the clip data functions
import clip as cl


os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles')
files = glob.glob('*poly*.shp')

Ada= gpd.read_file('Ada.shp') #-->GeoPandas dataframe
Ada= gpd.read_file('Ada_prj.shp') 
Ada=Ada.to_crs(epsg=32611) 

Jerome= gpd.read_file('Jerome.shp') #-->GeoPandas dataframe
Jerome=Jerome.to_crs(epsg=32611) 

poly = gpd.read_file(files[1]) #-->GeoPandas dataframe
poly=poly.to_crs(epsg=32611)

Ada_poly_1km=poly['geometry'].intersection(Ada)




Ada_poly_1km=cl.clip_shp(poly, Ada) #clip doesn't support multipolygons


# Plot the data
fig, ax = plt.subplots(figsize=(8, 8))
poly.plot(ax=ax,
         alpha=.9)
Ada.plot(alpha=.5,
            ax=ax)
Jerome.plot(alpha=.6,
            ax=ax)
plt.show()


