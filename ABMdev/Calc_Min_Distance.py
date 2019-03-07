#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:51:14 2019
Calculate distance to closest cell of a given land cover
@author: kek25
"""
import numpy as np
import math

samp=np.random.randint(low = 2, size=(5,6))
samp = np.array([[0,0,1,1,0,0],[0,0,0,1,0,0], [0,0,0,1,1,1], [0,0,0,0,1,0], [0,0,0,0,0,0]])

city = np.array(np.nonzero(samp))
other = np.array(np.where(samp==0))

#x=other[1,:]
#y=other[0,:]

d_temp = np.empty(city.shape[1]) #faster than zeros, but b careful!
minDist= np.empty(other.shape[1])
dist=np.zeros(samp.shape)
#turn into function
for i in np.arange(other.shape[1]):
  #go through each non-city cell
   x=other[1,i]
   y=other[0,i]
   
   #calculate distance to each of the city cells 
   for j in np.arange(city.shape[1]):
       xc=city[1,j]
       yc=city[0,j]
       
       if ((x == xc + 1 or x == xc -1 or x == xc) & (y == yc + 1 or y == yc -1 or y == yc)):
           d_temp[j] = 0
       elif (x == xc or y == yc):
           d_temp[j] = (abs(x-xc) + abs(y-yc)) - 1
       else: 
           d_temp[j] = math.sqrt((abs(x-xc)-1)**2 + (abs(y-yc)-1)**2)
           
       minDist[i] = min(d_temp)

   dist[y,x]=minDist[i]    
   
##########
# Import ada county 
####
    
   
import geopandas as gp

SRB_3km= gp.read_file('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles/SRB_gridpolys/SRB_poly_3km_V2.shp')
counties_shp= gp.read_file('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/CDL_analysis/Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
#clip SRB 3km to counties_shp where COUNTY_ALL == 18 for ADA
cities = gp.read_file('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/ABMdev/citylimits_Ada/citylimits.shp')
cities_grid =cities.ReadAsArray()
#convert from shapefile to raster w 1/0

