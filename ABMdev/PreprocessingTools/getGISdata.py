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
import rasterio
from rasterio.mask import mask
from rasterio import features
import pycrs
from shapely.ops import cascaded_union
import json

#set user directory
os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/')
DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/'
GCAMpath='/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/GCAM_SRP/'
#os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/')
#DataPath='/Users/kek25/Documents/GitRepos/IM3-BoiseState/'
GCAMpath='/Users/kek25/Dropbox/BSU/Python/IM3/GCAM_SRP/'

counties_shp= gp.read_file('GIS_anlaysis/Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')

#------------------------------------------------------------------------
# DEFINE FUNCTIONS
#------------------------------------------------------------------------

def getGISextent(countyList, scale):
    
    if scale == '3km':
        SRB_poly= gp.read_file(DataPath+'GIS_anlaysis/Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp') 
    elif scale == '1km':
        SRB_poly= gp.read_file(DataPath+'GIS_anlaysis/Shapefiles/SRB_gridpolys/SRB_poly_1km_V2.shp') 
    
    #select two shapefiles, this returns geometry of the union - this no longer distinguishes two
    extent=counties_shp['geometry'].loc[countyList].unary_union #this is the row index, not the "COUNTY_ALL" index
    extent_poly=SRB_poly[SRB_poly.geometry.intersects(extent)]
    return(extent_poly)
    

def getGCAM(countyList, year, scale): #returns a numpy array 

    data = rasterio.open(GCAMpath+'gcam_'+str(year)+'_srb_'+str(scale)+'.tiff') #this isn't working consistently ...?
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
    return(out_img) #this results in a 3D shape?


#tryin to figureout hoew to turn the shapefile with two counties into a raster   
def countyID(countyList, lc):
    
    extent_shp=counties_shp['geometry'].loc[countyList]#figuerout how to save the value that can go into the raster
    numCounties=len(extent_shp)
    es=gp.GeoDataFrame(extent_shp)
    es=es.assign(value=np.arange(numCounties)) #or figure out how to make up the values
    coords = [json.loads(extent_shp.to_json())['features'][0]['geometry']] 
    
    if numCounties > 1:
        for i in np.arange(1, numCounties):
            coords.append(json.loads(extent_shp.to_json())['features'][i]['geometry'])
  
    #this version dont work
   # coords =[json.loads(extent_shp.to_json())['features'][geom['geometry'] for geom in extent_shp] #parses features from GeoDataFrame the way rasterio wants them
    #shapes=features.shapes(extent_shp) input to this has to be a rasterio object
    out=features.rasterize(coords, lc[0].shape, fill=999, all_touched=False)
    
    return(out) 
#------------------------------------------------------------------------
# Select and save npy file of specific initialization year
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
year=2010
scale=1000


extent_poly=getGISextent(countyList, '1km')
gcam_init=getGCAM(countyList, year, scale)

extent_poly.to_file(DataPath+'ABMdev/Data/extent_1km_AdaCanyon.shp')
np.save(DataPath+'ABMdev/Data/gcam_1km_2010_AdaCanyon.npy', gcam_init) #not sure if this one needs to be changed ...
