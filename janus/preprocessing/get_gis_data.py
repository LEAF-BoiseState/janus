"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

Pre-process GIS data based on counties, base year, and resolution
"""

import os

import geopandas as gp

import janus.preprocessing.geofxns as gf
import janus.preprocessing.landcover_preprocessing as lc


def get_gis_data(counties_shp, categories_csv, county_list, scale, year, gcam_data_directory,
                 gcam_category_type='local_GCAM_id'):
    """Preprocess GIS data based on counties, base year, and resolution.

    :param counties_shp:                    Full path with file name and extension to the input counties shapefile.
    :type counties_shp:                     str

    :param categories_csv:                  Full path with file name and extension to the input categories CSV file
                                            that bins CDL landclasses to GCAM landclasses
    :type categories_csv:                   str

    :param county_list:                     List of county names to process
    :type county_list:                      list

    :param gcam_data_directory:             Full path to the directory containing the GCAM output raster
    :param gcam_data_directory:             str

    :param scale:                           resolution of grid cells in meters
    :type scale:                            int

    :param year:                            Four digit year to process (e.g., 2000)
    :type year:                             int

    :param gcam_category_type:              Convert CDL data to GCAM categories of choice, Default 'local_GCAM_id' which
                                            is a set of ids that are specific to a local set of crop categories; where,
                                            'GCAM_id_list' is the standard set of GCAM global categories.
    :type gcam_category_type:               str

    """

    # output directory
    # TODO:  change `os.path.dirname(gcam_data_directory)` to an output_path parameter that is passed into this fn.
    output_directory = os.path.dirname(gcam_data_directory)

    # read counties shapefile as geopandas data frame
    gdf_counties = gp.read_file(counties_shp)
    gdf_counties.set_index('county', inplace=True)

    # read in CDL to GCAM category key
    gdf_key = gp.read_file(categories_csv)

    # convert cdl data to GCAM categories of choice
    lc.c2g(gdf_key, gcam_category_type)

    # convert GCAM file to scale of interest
    lc.aggGCAM(scale, gcam_data_directory)

    # use the above file to create a polygon coverage
    lc.grid2poly(year, scale, gcam_data_directory, output_directory)

    # use the poly grid to create the extent for the model
    extent = gf.get_extent(counties_shp, county_list, scale, output_directory)

    # select initial gcam data from inital year
    lc_raster = gf.get_gcam(counties_shp, county_list, gcam_data_directory)

    return extent, lc_raster
