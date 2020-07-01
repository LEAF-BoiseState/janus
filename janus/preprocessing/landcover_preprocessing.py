"""
Created on Mon Nov 19 09:53:01 2018

@author: kek25

All functions necessary to do GIS pre-processing for Janus
"""

import gdal
import glob
import numpy as np
import geopandas as gp
import pandas as pd
import os
import json
from osgeo import osr
from joblib import Parallel, delayed
from shapely.geometry import Polygon, MultiPolygon
from fiona.crs import from_epsg
from rasterio.mask import mask
from shapely.ops import cascaded_union
import rasterio


# =============================================================================#
# PREAMBLE AND PATH DEFINITIONS
# =============================================================================#

class CdlDataStruct:
    """Attributes of input CDL data, location, file name, and all georeferencing information """

    # Constructor requires the path and file name of the input CDL data
    def __init__(self, cdl_path, cdl_infile):
        self.cdl_path = cdl_path
        self.cdl_infile = cdl_infile

    # Add CDL geographic transformation adn projection information
    def SetCDL_ProjInfo(self, GeoTransform, Projection, PixelSize):
        self.cdl_geotransform = GeoTransform
        self.cdl_projection = Projection
        self.cdl_pixelsize = PixelSize

    def SetCDLGrid(self, cdl_grid):  # Original CDL grid
        self.cdl_grid = cdl_grid

    def SetCDLStats(self, cdl_stats):  # Add CDL stats
        self.cdl_stats = cdl_stats


class gcam_dataStruct:

    def __init__(self, gcam_path, gcam_outfile):
        self.gcam_path = gcam_path
        self.gcam_outfile = gcam_outfile

    def SetGCAM_ProjInfo(self, GeoTransform, Projection, PixelSize):
        self.gcam_geotransform = GeoTransform
        self.gcam_projection = Projection
        self.gcam_pixelsize = PixelSize

    def SetGCAMStats(self, gcam_stats):  # Add GCAM stats
        self.gcam_stats = gcam_stats

    def SetGCAMGrid(self, gcam_grid):  # Add reclassified GCAM grid
        self.gcam_grid = gcam_grid


# =============================================================================#
# FUNCTION DEFINITIONS  
# =============================================================================#


def ReadArcGrid(cdl_struct):  # does the CDL path go in here??
    """ Reads in ArcGrid file for processing """

    # Construct the full name of the CDL input ArcGrid file
    cdl_file = os.path.join(cdl_struct.cdl_path, cdl_struct.cdl_infile)

    # Open the CDL input file using GDAL
    cdl_input = gdal.Open(cdl_file)
    cdl_struct.SetCDL_ProjInfo(cdl_input.GetGeoTransform(), cdl_input.GetProjection(), cdl_input.GetGeoTransform()[1])

    cdl_grid = np.float64(cdl_input.ReadAsArray())
    cdl_grid[cdl_grid == -9999] = np.nan
    cdl_struct.SetCDLGrid(cdl_grid)

    # Close CDL data set to save memory
    cdl_input = None

    return


def CDL2GCAM(cdl_struct, cdl_cat, gcam_struct, gcam_cat):
    """ Convert raster of CDL land cover to GCAM categories

    :param cdl_struct:      Raster of CDL land cover
    :type cdl_struct:       Class

    :param cdl_cat:         CDL input crop categories
    :type cdl_cat:          Vector

    :param gcam_struct:     Raster for GCAM land cover
    :type gcam_struct:      Class

    :param gcam_cat:        GCAM output crop categories
    :type gcam_cat:         Vector
    
    :return:                New land cover raster with GCAM categories
    :type:                  Class

    """

    cdl_stats = np.zeros(132)
    gcam_stats = np.zeros(28)

    gcam_grid = np.nan * np.ones(cdl_struct.cdl_grid.shape)  # new blank np array
    for i in np.arange(cdl_cat.size):  # unique cdl categories
        indx, indy = np.where(cdl_struct.cdl_grid == cdl_cat[i])
        gcam_grid[indx, indy] = gcam_cat[i]
        cdl_stats[i] = indx.size

    for i in np.arange(28):  # count of each gcam category
        indx, indy = np.where(gcam_grid == i + 1)
        gcam_stats[i] = indx.size

    cdl_struct.SetCDLStats(cdl_stats)

    gcam_struct.SetGCAM_ProjInfo(cdl_struct.cdl_geotransform, cdl_struct.cdl_projection, cdl_struct.cdl_pixelsize)
    gcam_struct.SetGCAMStats(gcam_stats)
    gcam_struct.SetGCAMGrid(gcam_grid)

    return


def saveGCAMGrid(gcam_struct):
    """ Creates outfile name, applies correct projection and saves raster

    :param gcam_struct:      Input GCAM structure
    :type:                   Class

    :return:                 Saved raster file
    :type:                   Tiff

    """

    gcam_grid = gcam_struct.gcam_grid
    nrows, ncols = np.shape(gcam_grid)

    gcam_outfile = os.path.join(gcam_struct.gcam_path, gcam_struct.gcam_outfile)

    gcam_driver = gdal.GetDriverByName('Gtiff')
    gcam_gdal = gcam_driver.Create(gcam_outfile, ncols, nrows, 1, gdal.GDT_Float32)

    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)  # Needed as an intermediate because no initial projection defined
    gcam_gdal.SetProjection(proj.ExportToWkt())
    gcam_gdal.SetGeoTransform(gcam_struct.gcam_geotransform)
    gcam_gdal.GetRasterBand(1).WriteArray(gcam_struct.gcam_grid)
    gdal.Warp(gcam_outfile, gcam_gdal, dstSRS='EPSG:32611')

    gcam_gdal.FlushCache()
    gcam_gdal = None

    return


def c2g(cdl_gcam_keyfile, gcam_output_path, cdl_input_path, conversion_id):
    """ Converts CDL categories to GCAM categories

    :param cdl_gcam_keyfile:    File that links CDL categories to new GCAM categories, users may modify this for
                                inclusion of local crops
    :type cdl_gcam_keyfile:     CSV

    :param gcam_output_path:    Path to save gcam output
    :type gcam_output_path:     String

    :param cdl_input_path:      Path to raw CDL data
    :type cdl_input_path:       String

    :param conversion_id:       String specifying which GCAM categories to use, options are 'local_GCAM_id' or 'GCAM_id'
                                for regular GCAM categories
    :type conversion_id:        String

    :return:                    Saved land cover rasters with user defined GCAM categories
    :type:                      Tiff
    """

    # =========================================================================#
    # 0. Read in category data and create vectors                             #
    # =========================================================================#

    cdl2gcam_key = pd.read_csv(cdl_gcam_keyfile, sep=',')
    cdl_cat = cdl2gcam_key['CDL_id'].values
    gcam_cat = cdl2gcam_key[conversion_id].values

    # =========================================================================#
    # 1. Initialize a list of CDL structures for analysis                     #
    # =========================================================================#
    files = glob.glob(os.path.join(cdl_input_path, 'cdl*.txt'))
    cdl_data = []
    gcam_data = []
    for file in files:
        # Initialize CDL data structures with paths and file names
        cdl_path = os.path.dirname(file)
        cdl_infile = os.path.basename(file)
        cdl_data.append(CdlDataStruct(cdl_path, cdl_infile))

        # Initialize GCAM data structures with paths and file names
        gcam_outfile = cdl_infile.replace('cdl', 'gcam')
        gcam_outfile = gcam_outfile.replace('txt', 'tiff')
        gcam_data.append(gcam_dataStruct(gcam_output_path, gcam_outfile))

    # =========================================================================#
    # 2a. Read in all the CDL files and store data in cdl_dataStruct          #
    # =========================================================================#
    Parallel(n_jobs=6, verbose=60, backend='threading')(delayed(ReadArcGrid)(cdl_data[i])
                                                        for i in np.arange(len(cdl_data)))

    # =========================================================================#
    # 2b. Perform the CDL-GCAM category conversion                            #
    # =========================================================================#
    Parallel(n_jobs=6, verbose=10, backend='threading')(delayed(CDL2GCAM)(cdl_data[i], cdl_cat, gcam_data[i], gcam_cat)
                                                        for i in np.arange(len(cdl_data)))

    # =========================================================================#
    # 2c. Save re categorized GCAM grids to files                              #
    # =========================================================================#
    Parallel(n_jobs=6, verbose=30, backend='threading')(delayed(saveGCAMGrid)(gcam_data[i])
                                                        for i in np.arange(len(cdl_data)))

    # =========================================================================#
    # 3. Create Arrays of Results
    # =========================================================================#
    f = len(files)
    cdl_stats = np.zeros((132, f))
    gcam_stats = np.zeros((28, f))

    for i in np.arange(f):
        cdl_stats[:, i] = cdl_data[i].cdl_stats
        gcam_stats[:, i] = gcam_data[i].gcam_stats
    np.savetxt(os.path.join(gcam_output_path, "cdl_initial.csv"), cdl_stats, delimiter=",")
    np.savetxt(os.path.join(gcam_output_path, "gcam_initial.csv"), gcam_stats, delimiter=",")


# =============================================================================#
# Aggregate to scale of interest
# =============================================================================#


def aggregate_grid(input_file, scale, year):
    """ Create grid that land cover data is saved in when aggregating from smaller scale to larger scale

    :param input_file:      Full path and filename of input land cover
    :type input_file:       String

    :param scale:           Resolution to aggregate data to in meters, suggested at 1000 or 3000
    :type scale:            Int

    :param year:            Year that land cover is being initialized from
    :type year:             Int

    :return:                New land cover raster at a specified resolution
    :type:                  Tiff

    """

    # Open the GeoTiff based on the input path and file
    src_ds = gdal.Open(input_file)

    # Create the name of the output file by modifying the input file
    gcam_write_file = 'gcam_' + str(int(scale)) + '_domain_' + str(int(year)) + '.tiff'

    # Get key info on the source data set    
    src_ncols = src_ds.RasterXSize
    src_nrows = src_ds.RasterYSize

    src_geot = src_ds.GetGeoTransform()
    src_proj = src_ds.GetProjection()
    src_res = src_ds.GetGeoTransform()[1]

    agg_factor = scale / src_res

    dst_ncols = int(src_ncols / agg_factor)
    dst_nrows = int(src_nrows / agg_factor)

    dst_driver = gdal.GetDriverByName('Gtiff')
    output = os.path.join(os.path.dirname(input_file), gcam_write_file)
    dst_ds = dst_driver.Create(output, dst_ncols, dst_nrows, 1, gdal.GDT_Float32)

    dst_geot = (src_geot[0], src_geot[1] * agg_factor, src_geot[2], src_geot[3], src_geot[4], src_geot[5] * agg_factor)

    dst_ds.SetGeoTransform(dst_geot)
    dst_ds.SetProjection(src_proj)

    gdal.ReprojectImage(src_ds, dst_ds, src_proj, src_proj, gdal.GRA_Mode)

    src_ds = None
    dst_ds = None

    return


# =============================================================================#
# Run aggregation function in parallel
# =============================================================================#


def aggGCAM(scale, lc_dir, year):
    """Runs aggregation function in parallel

    :param scale:        Resolution to aggregate data to in meters, suggested at 1000 or 3000
    :type scale:         Int

    :param lc_dir:       Directory where GCAM land cover data is stored
    :type lc_dir:        String

    :param year:         Year that land cover is being initialized from
    :type year:          Int

    :return:             saved land cover data at new resolution
    :type:               Tiff
    """

    gcam_read_files = glob.glob(os.path.join(lc_dir, 'gcam_' + str(int(year)) + '*.tiff'))

    Parallel(n_jobs=4, verbose=60, backend='threading')(delayed(aggregate_grid)(file, scale, year)
                                                        for file in gcam_read_files)


# =============================================================================#
# Create a set of polygons for entire domain
# =============================================================================#


def grid2poly(year, scale, gcam_dir, out_path):
    """Creates a grid of polygons for holding information in each cell

    :param year:        Initiation year for identifying GCAM raster
    :type year:         Int

    :param scale:       Scale of grid for identifying correct GCAM raster
    :type scale:        Int

    :param gcam_dir:    Location of GCAM file
    :type gcam_dir:     String

    :param out_path:    path for output file
    :type out_path:     String
    
    :return:            Saved grid of polygon
    :type:              ESRI Shapefile
    """

    grid_file = os.path.join(gcam_dir, 'gcam_' + str(int(scale)) + '_domain_' + str(int(year)) + '.tiff')

    src = gdal.Open(grid_file)
    srcarray = src.ReadAsArray().astype(np.float)

    x_index = np.arange(srcarray.shape[1])
    y_index = np.arange(srcarray.shape[0])
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = src.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2)  # add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2)  # to centre the point
    xc, yc = np.meshgrid(x_coords, y_coords)

    # create a list of all the polygons in the grid
    vert = list()
    for i in np.arange(srcarray.shape[1] - 1):
        for j in np.arange(srcarray.shape[0] - 1):
            vert.append([[xc[j, i], yc[j, i]], [xc[j + 1, i], yc[j + 1, i]], [xc[j + 1, i + 1], yc[j + 1, i + 1]],
                         [xc[j, i + 1], yc[j, i + 1]]])

    # create list of polygons
    polygons = [Polygon(vert[i]) for i in np.arange(len(vert))]

    # convert them to formats for exporting
    polys = gp.GeoSeries(MultiPolygon(polygons))
    polyagg = gp.GeoDataFrame(geometry=polys)
    polyagg.crs = from_epsg(32611)

    # -------------------------#
    # Save Output             #
    # -------------------------#
    out_file_name = os.path.join(out_path, 'domain_poly_' + str(int(scale)) + '.shp')
    polyagg.to_file(filename=out_file_name, driver="ESRI Shapefile")


# ============================================================================= #
#    Get extent of modeling domain                                              #
# ============================================================================= #


def get_extent(counties_shp, county_list, scale, out_path):
    """Create a grid of the extent based on counties and scale of interest.
    This will only be used if a user wants to use and clip other geospatial data such as elevation

    :param counties_shp:            Geopandas data frame of counties
    :type counties_shp:             Geopandas data frame

    :param county_list:             List of counties in the domain of interest
    :type county_list:              List of strings

    :param scale:                   Grid scale of output, can only be 3000 or 1000 (meters)
    :type scale:                    Int

    :param out_path:                File path to processed lc data folder
    :type out_path:                 String

    :return:                        Grid of polygons for the domain of interest
    :type:                          ESRI Shapefile
    """

    if scale == 3000:
        srb_poly = gp.read_file(os.path.join(out_path, 'domain_poly_3000.shp'))

    elif scale == 1000:
        srb_poly = gp.read_file(os.path.join(out_path, 'domain_poly_1000.shp'))

    # this returns geometry of the union, no longer distinguishes counties - see issue #1

    # this is the row index, not the "COUNTY_ALL" index
    extent = counties_shp['geometry'].loc[county_list].unary_union
    extent_poly = srb_poly[srb_poly.geometry.intersects(extent)]
    out_filename = 'extent_' + str(int(scale)) + '.shp'
    extent_poly.to_file(os.path.join(out_path, out_filename))


# ------------------------------------------------------------------------------------------------
#    Clip GCAM coverage to the counties of interest at scale of interest  & save for later use  #
# ------------------------------------------------------------------------------------------------

def get_gcam(counties_shp, county_list, gcam_path, out_path):
    """Clip GCAM coverage to the counties of interest at scale of interest.

    :param counties_shp:            Geopandas data frame for counties data
    :type counties_shp:             Geopandas data frame

    :param county_list:             List of counties in the domain of interest
    :type county_list:              List of strings

    :param gcam_path:               Full path with file name and extension to the GCAM raster
    :type gcam_path:                String

    :param out_path:                Path to the directory where the file will be saved for use in Janus
    :type out_path:                 String

    :return:                        Land cover data clipped to domain of interest
    :type:                          Tiff
    """

    data = rasterio.open(gcam_path)
    extent_shp = counties_shp['geometry'].loc[county_list]
    boundary = gp.GeoSeries(cascaded_union(extent_shp))
    coords = [json.loads(boundary.to_json())['features'][0][
                  'geometry']]  # parses features from GeoDataFrame the way rasterio wants them
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
    out_meta = data.meta.copy()

    # update metadata with new transformation information
    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform})

    # Merge original file name with init_landcover to denote that it is the initial land cover data for Janus
    in_file = os.path.basename(gcam_path)
    out_filename = os.path.join(out_path, 'init_landcover_' + in_file)

    # Save clipped land cover coverage
    out_tiff = rasterio.open(out_filename, 'w', **out_meta)
    out_tiff.write(np.squeeze(out_img, 0), 1)
    out_tiff.close()

    return
