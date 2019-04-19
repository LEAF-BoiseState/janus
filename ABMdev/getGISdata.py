#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

function that clips GIS data based on counties, year, and resolution
"""
import os  
import geopandas as gp

#set user directory
os.chdir('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/')
#os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/Shapefiles/')
DataPath= '/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/GIS_anlaysis/Shapefiles/'
GCAMpath='/Users/kek25/Dropbox/BSU/Python/IM3/GCAM_SRP/'

counties_shp= gp.read_file('Shapefiles/County_polys/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')


def getGISextent(countyList, scale):
    
    if scale == '3km':
        SRB_poly= gp.read_file(DataPath+'SRB_gridpolys/SRB_poly_3km_V2.shp') 
    elif scale == '1km':
        SRB_poly= gp.read_file(DataPath+'SRB_gridpolys/SRB_poly_1km_V2.shp') 
    
    #select two shapefiles, this returns geometry of the union - this no longer distinguishes two
    extent=counties_shp['geometry'].loc[countyList].unary_union #this is the row index, not the "COUNTY_ALL" index
    extent_poly=SRB_poly[SRB_poly.geometry.intersects(extent)]
    
    extent_poly.plot()
    return(extent_poly)
    #urban extent, and distance to city - done
    #area of influence
    #no-build mask
    #cdl data


def getGCAM(extent, year, scale):
    #use scale to dtermine which folder to id
    file=GCAMpath+scale+'/gcam_'+year




countyList=['Ada', 'Canyon']  
   
extent=getGISdata(countyList, '3km')
    #also this probably just needs to be a raster ... 
    