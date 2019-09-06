#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 15:09:10 2019

@author: kek25

Library of functions for geospatial processing

minDistCity - Calculates the distance from any cell to a city cell of any density category. It requires np.array of SRP GCAM categories, otherwise city cells will not be identified properly.
"""
import numpy as np
import geopandas as gp
import gdal
import rasterio
from rasterio.mask import mask
from shapely.geometry import Polygon, MultiPolygon 
from fiona.crs import from_epsg

import pycrs
from shapely.ops import cascaded_union
import json

#set paths
DataPath='~Data/'
GCAMpath='~Data/GCAM_SRP/'

counties_shp= gp.read_file('~Data/Counties/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')

#----------------------------------------------------------------------------
# DEFINE FUNCTIONS
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# Create a set of polygons for entire domain
#----------------------------------------------------------------------------

def grid2poly(grid_file, OutFileName):
    
    src= gdal.Open(DataPath+grid_file)
    srcarray = src.ReadAsArray().astype(np.float)

    x_index =np.arange(srcarray.shape[1]) 
    y_index = np.arange(srcarray.shape[0])
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = src.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2) #add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2) #to centre the point
    xc, yc = np.meshgrid(x_coords, y_coords)

    #create a list of all the polygons in the grid
    vert = list()
    for i in np.arange(srcarray.shape[1]-1):  
        for j in np.arange(srcarray.shape[0]-1):  
                vert.append([[xc[j, i] , yc[j,i]], [xc[j+1, i], yc[j+1, i]], [xc[j+1, i+1], yc[j+1, i+1]],[xc[j, i+1], yc[j, i+1]]])
 
    #create list of polygons
    polygons=[Polygon(vert[i]) for i in np.arange(len(vert))]

    #convert them to formats for exporting 
    polys   = gp.GeoSeries(MultiPolygon(polygons))
    polyagg = gp.GeoDataFrame(geometry=polys)
    polyagg.crs= from_epsg(32611)

    #-------------------------#
    # Save Output             #
    #-------------------------#
    polyagg.to_file(filename=DataPath+OutFileName, driver="ESRI Shapefile")



#----------------------------------------------------------------------------
# Create a grid of the extent based on counties and scale of interest
#----------------------------------------------------------------------------

def getGISextent(countyList, scale):
    
    if scale == 3000:
        SRB_poly= gp.read_file(DataPath+'SRB_poly_3km.shp') 
    elif scale == 1000:
        SRB_poly= gp.read_file(DataPath+'SRB_poly_1km.shp') 
    
    #select two shapefiles, this returns geometry of the union - this no longer distinguishes two - see issue #1
    extent=counties_shp['geometry'].loc[countyList].unary_union #this is the row index, not the "COUNTY_ALL" index
    extent_poly=SRB_poly[SRB_poly.geometry.intersects(extent)]
    return(extent_poly)
    
#----------------------------------------------------------------------------
# Clip GCAM coverage to the counties of interest at scale of interest
#----------------------------------------------------------------------------

def getGCAM(countyList, year, scale): #returns a numpy array 

    data = rasterio.open(GCAMpath+'gcam_'+str(year)+'_srb_'+str(scale)+'.tiff') #this isn't working consistently ...?
    extent_shp=counties_shp['geometry'].loc[countyList]
    boundary = gp.GeoSeries(cascaded_union(extent_shp))
    coords = [json.loads(boundary.to_json())['features'][0]['geometry']] #parses features from GeoDataFrame the way rasterio wants them
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
    out_meta = data.meta.copy()
    epsg_code = int(data.crs.data['init'][5:])
    
    out_meta.update({"driver": "GTiff",
                 "height": out_img.shape[1],
                 "width": out_img.shape[2],
                 "transform": out_transform,
                 "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
                        )
    return(out_img) 

#----------------------------------------------------------------------------
# Calculate the minimum distance to a city cell
#----------------------------------------------------------------------------
    
def minDistCity(gcam):
    
    #assert gcam.max <=28, "Array does not conform to SRP GCAM categories" had to remove, bc it was throwing error
    
    from scipy import spatial
    urban_bool= np.logical_or(np.logical_or(gcam[0] == 26, gcam[0] == 27), np.logical_or(gcam[0] == 17, gcam[0] == 25)) 
    
    rur=np.where(np.logical_and(~urban_bool, gcam[0] != 0)) 
    rural=np.array((rur[0],rur[1])).transpose()
    
    urb=np.where(urban_bool)
    urban = np.array((urb[0], urb[1])).transpose()
    
    tree = spatial.cKDTree(urban)
    mindist, minid = tree.query(rural)
    #reconstruct 2D np array with distance values
    urb_val=np.zeros(urban.shape[0])
    idx = np.vstack((urban, rural))
    dist= np.vstack((urb_val[:, None], mindist[:, None]))
    out=np.zeros(gcam[0].shape)
    out.fill(np.nan)
    for i in np.arange(dist.size):
        out[idx[i,0]][idx[i,1]]= dist[i]
    return(out)
    

    
    