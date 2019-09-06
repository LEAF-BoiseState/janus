#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

function that clips GIS data based on counties, year, and resolution
"""
 
import geopandas as gp
import numpy as np
import rasterio
from rasterio.mask import mask

import pycrs
from shapely.ops import cascaded_union
import json

#set paths
DataPath='~Data/'
GCAMpath='~Data/GCAM_SRP/'

counties_shp= gp.read_file('~Data/Counties/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')

#------------------------------------------------------------------------
# DEFINE FUNCTIONS
#------------------------------------------------------------------------

def getGISextent(countyList, scale):
    
    if scale == '3km':
        SRB_poly= gp.read_file(DataPath+'SRB_poly_3km.shp') 
    elif scale == '1km':
        SRB_poly= gp.read_file(DataPath+'SRB_poly_1km.shp') 
    
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
    return(out_img) 


#trying to  turn the shapefile with two counties into a raster   
def countyID(countyList, lc):
    
    extent_shp=counties_shp['geometry'].loc[countyList]#this is a geoseries, figuerout how to save the value that can go into the raster
    numCounties=len(extent_shp)
    es=gp.GeoDataFrame(extent_shp) #this is a geodataframe
    es=es.assign(value=np.arange(numCounties)) #add values to each shape

#### none of this works
   # coords = [json.loads(extent_shp.to_json())['features'][0]['geometry']]#parses features from GeoDataFrame the way rasterio wants them... hypothetically
    #if numCounties > 1:
     #   for i in np.arange(1, numCounties):
      #      coords.append(json.loads(extent_shp.to_json())['features'][i]['geometry'])
            
        #this version dont work
   #shapes=features.shapes(extent_shp) input to this has to be a rasterio object
   # coords[0]['coordinates'] - this is a list of 2 lists that have explicit coordinates of locations (pixels??)
    #shapes=features.shapes(coords[0]['coordinates']) #'list' object has no attribute 'dtype'
    #shapes=((geometry,value) for geometry, value in SOMETHING) #this creates a generator which is an iterable
    
    #outshape=(2809, 2838) # in the function it would be lc[0].shape
    #out=features.rasterize(shapes, outshape, fill=999, all_touched=False)
    
# this creates generator of geom, value pairs to use in rasterizing
    #shapes=((geometry,value) for geometry, value in es) #this creates a generator which is an iterable
    #(es['geometry'], 0) this results in a tuple - geoseries, value pair, Invalid geometry object at index 0
    #(es['geometry'][0], 0) this results in a tuple - polygon, value pair, int is not iterable
    #out = features.rasterize(shapes=es, out_shape=outshape, fill=999, all_touched=False)

  

    
    #return(out) 
#------------------------------------------------------------------------
# Select and save npy file of specific initialization year
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
year=2010
scale=3000


extent_poly=getGISextent(countyList, '3km')
gcam_init=getGCAM(countyList, year, scale)

extent_poly.to_file(DataPath+'extent_3km_AdaCanyon.shp')
np.save(DataPath+'gcam_3km_2010_AdaCanyon.npy', gcam_init) #not sure if this one needs to be changed ...




