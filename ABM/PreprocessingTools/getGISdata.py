#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

Pre-process GIS data based on counties, base year, and resolution
"""
 
import geofxns as gf
import cdl2gcam as c2g

#set paths
DataPath='../../Data/'
GCAMpath='../../Data/GCAM/'

#------------------------------------------------------------------------
# Select, crop and save npy file of specific initialization year and scale
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
scale=3000 #scale of grid in meters

gf.grid2poly(grid_file, 'domain_poly_'+str(int(scale))+'.shp')

extent=gf.getGISextent(countyList, scale)
#save extent
extent.to_file(DataPath+'extent_3km_AdaCanyon.shp')

#convert cdl data to GCAM categories of choice, this will take a while depending on size of original dataset
c2g.c2g(DataPath+'CDL2GCAM_SRP_categories.csv','SRP_GCAM_id') 

#convert GCAM file to scale of interest
c2g.aggGCAM(scale, GCAMpath)

#if additional geospatial data are avialable and included in model they can be 
#clipped and processed here using the extent file








