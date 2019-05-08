#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

function that clips GIS data based on counties, year, and resolution
"""
import os  
import geopandas as gp
import glob2 
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
import pycrs
from shapely.ops import cascaded_union

#set user directory
#os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
#DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
#GCAMpath='/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/GCAM_SRP/'
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
DataPath='/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
GCAMpath='/Users/kek25/Dropbox/BSU/Python/IM3/GCAM_SRP/'

counties_shp= gp.read_file('Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
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
    
    extent_poly.plot()
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
    show(out_img)
    #need to return this as a geo data frame? basically this will get updated, and then fed into the minDistCity function ... 
    return(out_img)



def minDistCity(gcam):
    
    from scipy import spatial
    urban_bool= np.logical_or(np.logical_or(gcam[0] == 26, gcam[0] == 27), np.logical_or(gcam[0] == 17, gcam[0] == 25)) 
    
    rur=np.where(np.logical_and(~urban_bool, gcam[0] != 0)) 
    rural=np.array((rur[0],rur[1])).transpose()
    
    urb=np.where(urban_bool)
    urban = np.array((urb[0], urb[1])).transpose()
    
    tree = spatial.cKDTree(urban)
    mindist, minid = tree.query(rural)
    #reconstruct 2D np array with distance values
    urb_val=np.zeros(urban.shape[0])
    idx = np.vstack((urban, rural))
    dist= np.vstack((urb_val[:, None], mindist[:, None]))
    out=np.zeros(gcam[0].shape)
    out.fill(np.nan)
    for i in np.arange(dist.size):
        out[idx[i,0]][idx[i,1]]= dist[i]
    
    return(out)
    



#TEST FUNCTIONS
import matplotlib.pyplot as plt

countyList=['Ada', 'Canyon']  
year=2014
scale=3000


extent_poly=getGISextent(countyList, '3km')
gcam=getGCAM(countyList, year, scale)
dist2city=minDistCity(gcam)

show(dist2city)
plt.colorbar()