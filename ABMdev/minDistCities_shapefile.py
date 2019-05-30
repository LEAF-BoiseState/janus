#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 11:38:40 2019

@author: kek25

This returns a shape file of polygons with values in it, not entirely working or what we need
"""

import os  
import geopandas as gp


#set user directory
#os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/'

counties_shp= gp.read_file('Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')

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
    


cities = gp.read_file(DataPath+'Shapefiles/COMPASS/CityLimits_AdaCanyon.shp') # ADD NEW CITIES SHP HERE 

fig, ax = plt.subplots(figsize = (10,10))
city_poly.plot(column='CITY', categorical =True, ax=ax)
rural.plot(column='distCity', legend = True, ax=ax)
counties.plot()