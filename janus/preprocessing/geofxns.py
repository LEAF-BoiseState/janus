#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 15:09:10 2019

@author: kek25

Library of functions for geospatial processing
"""

import numpy as np
import geopandas as gp
import rasterio
import pycrs
import json
import urllib

from rasterio.mask import mask
from shapely.ops import cascaded_union
from scipy import spatial


def get_extent(counties_shp, county_list, scale, DataPath):
    """Create a grid of the extent based on counties and scale of interest. 
    This will be used if a user want to use and clip other geospatial data such as elevation

    :param counties_shp:                Geopandas data frame for counties data
    :param county_list:                 List of counties in the domain of interest
    :param scale:                       Grid scale of output, can only be 3000 or 1000 (meters)
    :param DataPath:                    File path to data folder

    :return:                            Grid of polygons for the domain of interest
    """
    
    if scale == 3000:
        SRB_poly = gp.read_file(DataPath+'domain_poly_3000.shp')

    elif scale == 1000:
        SRB_poly = gp.read_file(DataPath+'domain_poly_1000.shp')
    
    # this returns geometry of the union, no longer distinguishes counties - see issue #1

    # this is the row index, not the "COUNTY_ALL" index
    extent=counties_shp['geometry'].loc[county_list].unary_union
    extent_poly = SRB_poly[SRB_poly.geometry.intersects(extent)]
    
    extent_poly.to_file(DataPath+'extent_'+str(int(scale))+'.shp')

    return extent_poly
    

def get_gcam(counties_shp, county_list, gcam_file):
    """Clip GCAM coverage to the counties of interest at scale of interest.

    :param counties_shp:                Geopandas data frame for counties data
    :param countyList:                  List of counties in the domain of interest
    :param year:                        Year of GCAM data to initalize with, used to identify file name
    :param scale:                       Scale of grid cells, used to identify file name
    :param gcam_file:                   Full path with file name and extension to the GCAM raster

    :return:                            Landcover data clipped to domain of interest

    """

    data = rasterio.open(gcam_file) 
    extent_shp = counties_shp['geometry'].loc[county_list]
    boundary = gp.GeoSeries(cascaded_union(extent_shp))
    coords = [json.loads(boundary.to_json())['features'][0]['geometry']] # parses features from GeoDataFrame the way rasterio wants them
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
    out_meta = data.meta.copy()
    epsg_code = int(data.crs.data['init'][5:])

    # TODO:  check to see if this is a vaild workaround for not setting a coordinate system on failure
    try:
        fetch_crs = pycrs.parse.from_epsg_code(epsg_code).to_proj4()

    except urllib.error.URLError:
        fetch_crs = None

    out_meta.update({"driver": "GTiff",
                 "height": out_img.shape[1],
                 "width": out_img.shape[2],
                 "transform": out_transform,
                 "crs": fetch_crs})
    return out_img


def min_dist_city(gcam):
    """Calculate the minimum distance to a city cell.

    :param gcam: np.array of land cover of Snake River Basin GCAM categories, other key files will incorrectly identify city cells

    :return: np.array of distance to a city cell within the domain

    """
    # TODO:  update to be based on key file (local_cat == urb)
    urban_bool = np.logical_or(np.logical_or(gcam == 26, gcam == 27), np.logical_or(gcam == 17, gcam == 25))
    
    rur = np.where(np.logical_and(~urban_bool, gcam != 0))
    rural = np.array((rur[0], rur[1])).transpose()
    
    urb = np.where(urban_bool)
    urban = np.array((urb[0], urb[1])).transpose()
    
    tree = spatial.cKDTree(urban)
    mindist, minid = tree.query(rural)

    # reconstruct 2D np array with distance values
    urb_val = np.zeros(urban.shape[0])
    idx = np.vstack((urban, rural))
    dist = np.vstack((urb_val[:, None], mindist[:, None]))
    out = np.zeros(gcam.shape)
    out.fill(np.nan)

    for i in np.arange(dist.size):
        out[idx[i, 0]][idx[i, 1]] = dist[i]

    return out
