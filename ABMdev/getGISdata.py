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
#set user directory
os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
#os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/Shapefiles/')
DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'
#GCAMpath='/Users/kek25/Dropbox/BSU/Python/IM3/GCAM_SRP/'
GCAMpath='/Users/kendrakaiser/Volumes/GFS_RAID/Dropbox/BSU/Python/IM3/GCAM_SRP/'

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
    #urban extent, and distance to city - done
    #area of influence
    #no-build mask
    #cdl data

year=2014
scale=3000

def getGCAM(extent, year, scale):
    file=glob2.glob('GCAM_SRP/gcam_'+str(year)+'_srb_'+str(scale)+'.tiff')
    gcam_dat=gdal.Open(DataPath+file[0])
    ds= gcam_dat.GetRasterBand(1)
    ds_grid = np.float64(ds.ReadAsArray())


    
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

    return(rural,city_poly)
    #return(SRB_city_poly)




#TEST FUNCTIONS
import matplotlib.pyplot as plt
#cities = gp.read_file(DataPath+'Cities/SRB_cities.shp') 
cities = gp.read_file(DataPath+'Shapefiles/COMPASS/CityLimits_AdaCanyon.shp') # ADD NEW CITIES SHP HERE 

countyList=['Ada', 'Canyon']  
 
extent_poly=getGISextent(countyList, '3km')
    #also this probably just needs to be a raster ... 
out=minDistCity(cities, '3km', extent)

fig, ax = plt.subplots(figsize = (10,10))
city_poly.plot(column='CITY', categorical =True, ax=ax)
rural.plot(column='distCity', legend = True, ax=ax)


fig, ax = plt.subplots(figsize=(10, 8))
ax.imshow(gcam_im, cmap='terrain')
extent.plot(ax=ax, alpha=.8)
ax.set_title("Raster Layer with Shapefile Overlayed")
ax.set_axis_off()