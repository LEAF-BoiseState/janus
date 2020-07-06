"""
Created on Mon Apr  8 21:55:00 2019

@author: kek25

Select GIS data based on base year, and resolution and clip to extent to create the initial land cover coverage
"""

import os
import geopandas as gp
import janus.preprocessing.landcover_preprocessing as lc


def get_gis_data(counties_shp, categories_csv, county_list, scale, year, raw_lc_dir, processed_lc_dir, init_lc_dir,
                 gcam_category_type='local_GCAM_id'):
    """Pre-process GIS data based on counties, base year, and resolution.

    :param counties_shp:                    Full path with file name and extension to the input counties shapefile.
    :type counties_shp:                     str

    :param categories_csv:                  Full path with file name and extension to the input categories CSV file
                                            that bins CDL land classes to GCAM land classes
    :type categories_csv:                   str

    :param county_list:                     List of county names to process
    :type county_list:                      list

    :param scale:                           resolution of grid cells in meters
    :type scale:                            int

    :param year:                            Four digit year to process (e.g., 2000)
    :type year:                             int

    :param raw_lc_dir:                      Full path to the directory containing the raw land cover data
    :type raw_lc_dir:                       str

    :param processed_lc_dir:                Full path to the directory containing the processed land cover data
    :type processed_lc_dir:                 str

    :param init_lc_dir:                     Full path to the directory where land cover initialization files are stored
    :type init_lc_dir:                      str

    :param gcam_category_type:              Convert CDL data to GCAM categories of choice, Default 'local_GCAM_id' which
                                            is a set of ids that are specific to a local set of crop categories; where,
                                            'GCAM_id_list' is the standard set of GCAM global categories.
    :type gcam_category_type:               str

    :return:                                [0] Tiff; Land cover in GCAM categories at scale of input data
                                            [1] Tiff; Land cover in GCAM categories at user defined scale of interest
                                            [2] ESRI Shapefile; Extent of domain
                                            [3] ESRI Shapefile; grid of polygons for domain
                                            [4] Tiff; GCAM land cover for initiation year clipped to user defined extent


    """
    # read counties shapefile as geopandas data frame
    gdf_counties = gp.read_file(counties_shp)
    gdf_counties.set_index('county', inplace=True)

    # convert cdl data to GCAM categories of choice
    lc.c2g(categories_csv, processed_lc_dir, raw_lc_dir, gcam_category_type)

    assert os.path.exists(os.path.join(processed_lc_dir, 'gcam_'+str(int(year))+'_srb.tiff')), \
        'get_gis_data.py ERROR: CDL to GCAM conversion was not successful, output does not exist'

    # convert GCAM file to scale of interest
    lc.agg_gcam(scale, processed_lc_dir, year)

    assert os.path.exists(
        os.path.join(processed_lc_dir, 'gcam_' + str(int(scale)) + '_domain_' + str(int(year)) + '.tiff')), \
        'get_gis_data.py ERROR: aggregation was not successful, output does not exist'

    # use the above file to create a polygon coverage & save; this allows for mapping each cell over time (?)
    lc.grid2poly(year, scale, processed_lc_dir, init_lc_dir)

    # use the poly grid to create the extent for the model - only needed if using other land cover data
    lc.get_extent(gdf_counties, county_list, scale, init_lc_dir)

    # crop land cover data from initialization year
    gcam_file = os.path.join(processed_lc_dir, 'gcam_' + str(int(scale)) + '_domain_' + str(int(year)) + '.tiff')
    lc.get_gcam(gdf_counties, county_list, gcam_file, init_lc_dir)

    assert os.path.exists(os.path.join(init_lc_dir, 'init_landcover_' + os.path.basename(gcam_file))), \
        'get_gis_data.py ERROR: clipping to user extent was not successful, output does not exist'
