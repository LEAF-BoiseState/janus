#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

function that clips GIS data based on counties, year, and resolution
"""
import os  
import geopandas as gp
import numpy as np
import glob2 
import rasterio
from rasterio.mask import mask
import pycrs
from shapely.ops import cascaded_union

#set user directory
#os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
#DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
#GCAMpath='/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/GCAM_SRP/'
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/')
DataPath='/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
GCAMpath='/Users/kek25/Dropbox/BSU/Python/IM3/GCAM_SRP/'

counties_shp= gp.read_file('GIS_anlaysis/Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')

#------------------------------------------------------------------------
# DEFINE FUNCTIONS
#------------------------------------------------------------------------

def getGISextent(countyList, scale):
    
    if scale == '3km':
        SRB_poly= gp.read_file(DataPath+'Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp') 
    elif scale == '1km':
        SRB_poly= gp.read_file(DataPath+'Shapefiles/SRB_gridpolys/SRB_poly_1km_V2.shp') 
    
    #select two shapefiles, this returns geometry of the union - this no longer distinguishes two
    extent=counties_shp['geometry'].loc[countyList].unary_union #this is the row index, not the "COUNTY_ALL" index
    extent_poly=SRB_poly[SRB_poly.geometry.intersects(extent)]
    return(extent_poly)
    

def getGCAM(countyList, year, scale): #returns a numpy array 
    import json #whats the diff btw importing libraries here v in main environ?
    file=glob2.glob(GCAMpath+'gcam_'+str(year)+'_srb_'+str(scale)+'.tiff') #other way to use this other than glob?? 

    data = rasterio.open(file[0])
    extent_shp=counties_shp['geometry'].loc[countyList]
    boundary = gp.GeoSeries(cascaded_union(extent_shp))
    coords = [json.loads(boundary.to_json())['features'][0]['geometry']] #parses features from GeoDataFrame the way rasterio wants them
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
    out_meta = data.meta.copy()
    epsg_code = int(data.crs.data['init'][5:])
    
    out_meta.update({"driver": "GTiff",
                 "height": out_img.shape[1],
                 "width": out_img.shape[2],
                 "transform": out_transform,
                 "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
                        )
    return(out_img)

#------------------------------------------------------------------------
# Select and save npy file of specific initialization year
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
year=2010
scale=1000


extent_poly=getGISextent(countyList, '1km')
gcam_init=getGCAM(countyList, year, scale)

np.save('/ABMdev/Data/extent.npy', extent_poly)
np.save('/ABMdev/Data/gcam_1km_2010_AdaCanyon.npy', gcam_init)
