#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:51:14 2019
Calculate distance to closest cell of a given land cover
@author: kek25
"""
    
import os  
import geopandas as gp
import numpy as np

#set user directory
#os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/')
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/')

SRB_3km= gp.read_file('CDL_analysis/Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
counties_shp= gp.read_file('CDL_analysis/Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
cities = gp.read_file('ABMdev/citylimits_Ada/citylimits.shp')
cities=cities.to_crs(counties_shp.crs) #convert projection

#select unique COUNTIES from SRB3km_poly * change the code here when we have all counties city info
Ada_3km=SRB_3km[SRB_3km.geometry.intersects(counties_shp['geometry'][17])]
Canyon_3km=SRB_3km[SRB_3km.geometry.intersects(counties_shp['geometry'][12])]

#you can select two shapefiles, but need to return geometry of the union - this no longer distinguishes two
AC=counties_shp['geometry'][[12,17]].unary_union #this is the row index, not the "COUNTY_ALL" index
Ada_Canyon=SRB_3km[SRB_3km.geometry.intersects(AC)]
Ada_Canyon.plot()

Ada_3km.plot()
Canyon_3km.plot()
cities.plot()

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize = (5,5))
Ada_3km.plot(ax=ax, 
             color = 'green')
Canyon_3km.plot(ax=ax,
                color ='blue')
#PROBLIMATIC - OVERLAPPING EDGES OF COUNTIES


#join the cities data with the clipped ada county polygons
Ada_cities_3km=gp.sjoin(Ada_3km, cities[['CITY', 'geometry']], how = 'left', op='intersects')
#replace Nas
Ada_cities_3km['index_right']=Ada_cities_3km['index_right'].fillna(99)
Ada_cities_3km['CITY']=Ada_cities_3km['CITY'].fillna('Rural')
Ada_cities_3km.plot(column='CITY', categorical =True, legend=True, figsize=(5,10))

Ada_cities_3km['index_right'].plot()

#SUBSET INTO SEPERATE SHAPEFILES to calculate distance
Ada_rural=Ada_cities_3km[Ada_cities_3km['CITY'] == 'Rural']
Ada_cities=Ada_cities_3km[Ada_cities_3km['CITY'] != 'Rural']
#calculate distance to closest city
Ada_rural['distCity'] = Ada_rural.geometry.apply(lambda g: Ada_cities.distance(g).min())

fig, ax = plt.subplots(figsize = (5,10))
Ada_rural.plot(column='distCity', legend = True, figsize=(5,10), ax=ax)
Ada_cities.plot(color='orange', ax=ax)


##RECOMBINING THEM DOESNT WORK YET
if Ada_cities_3km[Ada_cities_3km['CITY'] == 'Rural']:
    Ada_cities_3km['distCity'] = 0
else: Ada_cities_3km['distCity'] = Ada_rural['distCity']
