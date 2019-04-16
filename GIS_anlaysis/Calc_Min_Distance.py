#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:51:14 2019
Calculate distance to closest cell of a given land cover
@author: kek25
"""
    
import os  
import geopandas as gp

#set user directory
os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles/')
#os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles/')

SRB_3km= gp.read_file('SRB_gridpolys/SRB_poly_3km_V2.shp')
counties_shp= gp.read_file('County_polys/Counties_SRB_clip_SingleID.shp')
cities = gp.read_file('COMPASS/CityLimits_AdaCanyon.shp')
cities=cities.to_crs(counties_shp.crs) #convert projection
cities.plot()
#select unique COUNTIES from SRB3km_poly * change the code here when we have all counties city info
#Ada_3km=SRB_3km[SRB_3km.geometry.intersects(counties_shp['geometry'][17])]
#Canyon_3km=SRB_3km[SRB_3km.geometry.intersects(counties_shp['geometry'][12])]
#fig, ax = plt.subplots(figsize = (5,5))
#Ada_3km.plot(ax=ax, color = 'green')
#Canyon_3km.plot(ax=ax,color ='blue')
#PROBLIMATIC - OVERLAPPING EDGES OF COUNTIES

#you can select two shapefiles, but need to return geometry of the union - this no longer distinguishes two
AC=counties_shp['geometry'][[12,17]].unary_union #this is the row index, not the "COUNTY_ALL" index
Ada_Canyon=SRB_3km[SRB_3km.geometry.intersects(AC)]
#also this probably just needs to be a raster ... 
Ada_Canyon.plot()

import matplotlib.pyplot as plt

#join the cities data with the clipped ada county polygons
AC_cities_3km=gp.sjoin(Ada_Canyon, cities[['CITY', 'geometry']], how = 'left', op='intersects')
#replace Nas
AC_cities_3km['index_right']=AC_cities_3km['index_right'].fillna(99)
AC_cities_3km['CITY']=AC_cities_3km['CITY'].fillna('Rural')

AC_cities_3km.plot(column='CITY', categorical =True, legend=True, figsize=(5,10))

#SUBSET INTO SEPERATE SHAPEFILES to calculate distance
AC_rural=AC_cities_3km[AC_cities_3km['CITY'] == 'Rural']
AC_cities=AC_cities_3km[AC_cities_3km['CITY'] != 'Rural']
AC_rural=AC_rural.rename(columns={'index_right':'city_index'})
AC_cities=AC_cities.rename(columns={'index_right':'city_index'})

#calculate distance to closest city
AC_rural['distCity'] = AC_rural.geometry.apply(lambda g: AC_cities.distance(g).min())
AC_cities['distCity']=0

fig, ax = plt.subplots(figsize = (10,10))
AC_rural.plot(column='distCity', legend = True, figsize=(5,10), ax=ax)
AC_cities.plot(column='distCity', ax=ax)

AC_rural.to_file(driver='ESRI Shapefile', filename='AC_ruralDist_3000.shp')
AC_cities.to_file(driver='ESRI Shapefile', filename='AC_cities_3000.shp')

##CANT Figure out how to combine them yet - and these should eb as rasters, rather than shapefiles .... THEM DOESNT WORK YET
AC = gp.sjoin(AC_rural, AC_cities[:], op= 'intersects')
AC=gp.overlay(AC_rural, AC_cities, how= 'union')




