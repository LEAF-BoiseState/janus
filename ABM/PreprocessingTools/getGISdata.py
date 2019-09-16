#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

Pre-process GIS data based on counties, base year, and resolution
"""
 
import geofxns as gf
import numpy as np

#set paths
DataPath='~Data/'
GCAMpath='~Data/GCAM_SRP/'

#------------------------------------------------------------------------
# Select and save npy file of specific initialization year
#------------------------------------------------------------------------

countyList=['Ada', 'Canyon']  
year=2010
scale=3000

extent_poly=gf.getGISextent(countyList, scale)

gcam_init=gf.getGCAM(countyList, year, scale)

extent_poly.to_file(DataPath+'extent_3km_AdaCanyon.shp')
np.save(GCAMpath+'gcam_3km_2010_AdaCanyon.npy', gcam_init) #not sure if this one needs to be changed ...




