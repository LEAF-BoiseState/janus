#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:51:14 2019
Calculate distance to closest cell of a given land cover
@author: kek25
"""
    
import os  
import geopandas as gp
import matplotlib.pyplot as plt

#set user directory
#os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_analysis/Shapefiles/')
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/Shapefiles/'

#cities = gp.read_file(DataPath+'Cities/SRB_cities.shp') 
cities = gp.read_file(DataPath+'COMPASS/CityLimits_AdaCanyon.shp') # ADD NEW CITIES SHP HERE 


extent=getGISdata(countyList, '3km')

#scale should be '3km' or '1km'

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


out=minDistCity(cities, '3km', extent)

fig, ax = plt.subplots(figsize = (10,10))
city_poly.plot(column='CITY', categorical =True, ax=ax)
rural.plot(column='distCity', legend = True, ax=ax)



#AC = gp.sjoin(SRB_rural,city_poly[:], op= 'intersects')
#AC=gp.overlay(SRB_rural,city_poly, how= 'union')




