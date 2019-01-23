#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 17:54:39 2018

@author: kek25
"""
import os
import glob
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from rasterio.plot import show
from shapely.geometry import mapping

os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles')

Ada = gpd.read_file('Ada.shp') #-->GeoPandas dataframe
Ada=Ada.to_crs(epsg=32611) #reproject bc for some reason not saving the crs from Arc

os.chdir('/Users/kendrakaiser/Documents/Data/GCAM_UTM/1km')
files = glob.glob('*.tiff')


with rio.open(files[0]) as src:
    extent_geojson = mapping(Ada['geometry'][0])
    Ada_cdl, affine = mask(src, 
                            [extent_geojson], 
                            crop=True)
    # metadata for writing or exporting the data
    Ada_meta = src.meta.copy()
    Ada_meta.update({"driver": "GTiff",
                     "height": Ada_cdl.shape[1],
                     "width": Ada_cdl.shape[2],
                     "transform": affine,
                     "crs":32611})

    show(Ada_cdl)
    
# Write data
writeDir='/Users/kendrakaiser/Documents/Data/GCAM_UTM/1km/Ada/'
writeFile = files[0].replace('srb','Ada')
with rio.open(writeDir+writeFile, 'w', **Ada_meta) as out:
    out.write(Ada_cdl)
