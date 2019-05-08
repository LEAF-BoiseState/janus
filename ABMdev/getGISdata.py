#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

function that clips GIS data based on counties, year, and resolution
"""
import os  
import geopandas as gp
import gdal
import glob2 
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
import pycrs
from shapely.ops import cascaded_union

#set user directory
os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
#os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
#DataPath='/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
#GCAMpath='/Users/kek25/Dropbox/BSU/Python/IM3/GCAM_SRP/'
GCAMpath='/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/GCAM_SRP/'

counties_shp= gp.read_file('Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')



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
 


year=2014
scale=3000


#https://automating-gis-processes.github.io/CSC/notebooks/L5/clipping-raster.html
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


    
def minDistCity(cityShape, scale, extent_poly):
    
    cities=cityShape.to_crs(extent_poly.crs) #convert projection - do this somewhere else?
    #join the cities data with the SRB polygons
    city_poly=gp.sjoin(extent_poly, cities[['CITY', 'geometry']], how = 'left', op='intersects')
    #replace Nas
    city_poly['index_right']=city_poly['index_right'].fillna(99)
    city_poly['CITY']=city_poly['CITY'].fillna('Rural')

    #city_poly.plot(column='CITY', categorical =True, legend=True, figsize=(5,10))

    #SUBSET INTO SEPERATE SHAPEFILES to calculate distance
    rural=city_poly[city_poly['CITY'] == 'Rural']
    city=city_poly[city_poly['CITY'] != 'Rural']
    rural=rural.rename(columns={'index_right':'city_index'})
    city=city.rename(columns={'index_right':'city_index'})

    #calculate distance to closest city
    rural['distCity'] =rural.geometry.apply(lambda g:city.distance(g).min())
    city['distCity']=0
    
    
    #now add column back to main coverage THIS DOESNT WORK
    #SRB_city_poly[SRB_city_poly['id'] ==rural['id']]['distCity']=rural['distCity']
    
    rural_filename = 'ruralDist_'+ scale +'.shp'
    ##CANT Figure out how to combine them yet - and should they be rasters, rather than shapefiles?
    rural.to_file(driver='ESRI Shapefile', filename=rural_filename)

    return(rural,city_poly) #this only returns rural, need to join the two back together ... 
    #return(SRB_city_poly)


def minDistCityg(gcam):
    
    from scipy import spatial
    urban_bool= np.logical_or(np.logical_or(gcam[0] == 26, gcam[0] == 27), np.logical_or(gcam[0] == 17, gcam[0] == 25)) 
    rur=np.where(~urban_bool)
    rural=np.array((rur[0],rur[1])).transpose()
    
    urb=np.where(urban_bool)
    urban = np.array((urb[0], urb[1])).transpose()
    
    tree = spatial.cKDTree(urban)
    mindist, minid = tree.query(rural)
    #reconstruct 2D np array with distance values
    urb_val=np.zeros(urban.shape[0])
    idx = np.vstack((urban, rural))
    dist= np.vstack((urb_val[:, None], mindist[:, None]))
    

    
    return(mindist)
    



#TEST FUNCTIONS
import matplotlib.pyplot as plt
#cities = gp.read_file(DataPath+'Cities/SRB_cities.shp') 
cities = gp.read_file(DataPath+'Shapefiles/COMPASS/CityLimits_AdaCanyon.shp') # ADD NEW CITIES SHP HERE 

countyList=['Ada', 'Canyon']  
 
extent_poly=getGISextent(countyList, '3km')
gcam=getGCAM(countyList, year, scale)

    #also this probably just needs to be a raster ... 
out=minDistCity(cities, '3km', extent_poly)

fig, ax = plt.subplots(figsize = (10,10))
city_poly.plot(column='CITY', categorical =True, ax=ax)
rural.plot(column='distCity', legend = True, ax=ax)
counties.plot()

fig, ax = plt.subplots(figsize=(10, 8))
ax.imshow(gcam_im, cmap='terrain')
extent.plot(ax=ax, alpha=.8)
ax.set_title("Raster Layer with Shapefile Overlayed")
ax.set_axis_off()