#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

function that clips GIS data based on counties, year, and resolution
"""

def getGISdata(countyList, year, scale):
    #urban extent
    #area of influence
    #distance to city
    #no-build mask
    #cdl data
    
    
    counties_shp= gp.read_file('County_polys/Counties_SRB_clip_SingleID.shp')
    #select two shapefiles, this returns geometry of the union - this no longer distinguishes two
    AC=counties_shp['geometry'][[12,17]].unary_union #this is the row index, not the "COUNTY_ALL" index
    Ada_Canyon=SRB_3km[SRB_3km.geometry.intersects(AC)]
    #also this probably just needs to be a raster ... 
    Ada_Canyon.plot()