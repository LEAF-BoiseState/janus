#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

Pre-process GIS data based on counties, base year, and resolution
"""
 
import geofxns as gf
import landcoverPreProcessingfxns as lc
import geopandas as gp
import csv
#set paths
DataPath='../Data/'
GCAMpath='.../Data/GCAM/'


counties_shp= gp.read_file(DataPath+'Counties/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')

key_file=csv.reader(DataPath+'CDL2GCAM_SRP_categories.csv', delimiter=',')

#------------------------------------------------------------------------
# Select, crop and save npy file of specific initialization year and scale
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
scale=3000 #scale of grid in meters
year=2010

#convert cdl data to GCAM categories of choice, this will take a while depending on size of original dataset
lc.c2g(key_file,'SRP_GCAM_id') 

#convert GCAM file to scale of interest
lc.aggGCAM(scale, GCAMpath)

#use the above file to create a polygon coverage

gf.grid2poly(year, scale, GCAMpath, DataPath)

#use the poly grid to create the extent for the model
extent=gf.getExtent(counties_shp, countyList, scale, DataPath)
#save extent


#select initial gcam data from inital year 
lc=gf.getGCAM(counties_shp, countyList, year, scale, GCAMpath)



#if additional geospatial data are avialable and included in model they can be 
#clipped and processed here using the extent file








