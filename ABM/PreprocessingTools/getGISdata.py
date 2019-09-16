#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

Pre-process GIS data based on counties, base year, and resolution
"""
 
import geofxns as gf
import numpy as np
import cdl2gcam as c2g
import AggregateGCAMGrids as agg

#set paths
DataPath='../../Data/'
GCAMpath='../../Data/GCAM/'

#------------------------------------------------------------------------
# Select, crop and save npy file of specific initialization year and scale
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
year=2010
scale=3000 #scale of grid in meters

#create the grid based on extent of counties and scale
extent_poly=gf.getGISextent(countyList, scale)

#convert cdl data to GCAM categories of choice
c2g.c2g(DataPath+'CDL2GCAM_SRP_categories.csv','SRP_GCAM_id') #works through here!!!

#convert GCAM file to scale of interest
agg.aggGCAM(scale, GCAMpath)

#select gcam data from inital year
gcam_init=gf.getGCAM(countyList, year, scale)

#save files
extent_poly.to_file(DataPath+'extent_3km_AdaCanyon.shp')
np.save(GCAMpath+'gcam_3km_2010_AdaCanyon.npy', gcam_init)




