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
os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/Shapefiles/')

SRB_3km= gp.read_file('SRB_gridpolys/SRB_poly_3km_V2.shp')
cities = gp.read_file('COMPASS/CityLimits_AdaCanyon.shp') # ADD NEW CITIES SHP HERE 
cities=cities.to_crs(SRB_3km.crs) #convert projection
cities.plot()

#join the cities data with the SRB polygons
SRB_cities_3km=gp.sjoin(SRB_3km, cities[['CITY', 'geometry']], how = 'left', op='intersects')
#replace Nas
SRB_cities_3km['index_right']=SRB_cities_3km['index_right'].fillna(99)
SRB_cities_3km['CITY']=SRB_cities_3km['CITY'].fillna('Rural')

SRB_cities_3km.plot(column='CITY', categorical =True, legend=True, figsize=(5,10))

#SUBSET INTO SEPERATE SHAPEFILES to calculate distance
SRB_rural=SRB_cities_3km[SRB_cities_3km['CITY'] == 'Rural']
SRB_cities=SRB_cities_3km[SRB_cities_3km['CITY'] != 'Rural']
SRB_rural=SRB_rural.rename(columns={'index_right':'city_index'})
SRB_cities=SRB_cities.rename(columns={'index_right':'city_index'})

#calculate distance to closest city
SRB_rural['distCity'] = SRB_rural.geometry.apply(lambda g: SRB_cities.distance(g).min())
SRB_cities['distCity']=0

fig, ax = plt.subplots(figsize = (10,10))
SRB_rural.plot(column='distCity', legend = True, figsize=(5,10), ax=ax)
SRB_cities.plot(column='distCity', ax=ax)

SRB_rural.to_file(driver='ESRI Shapefile', filename='SRB_ruralDist_3000.shp')
SRB_cities.to_file(driver='ESRI Shapefile', filename='SRB_cities_3000.shp')

##CANT Figure out how to combine them yet - and these should eb as rasters, rather than shapefiles .... THEM DOESNT WORK YET
AC = gp.sjoin(SRB_rural, SRB_cities[:], op= 'intersects')
AC=gp.overlay(SRB_rural, SRB_cities, how= 'union')




