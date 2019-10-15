"""
Created on Mon Nov 19 09:53:01 2018

@author: kek25
"""

import gdal
import glob 
import numpy as np
from joblib import Parallel, delayed
import pandas as pd
import os
from osgeo import osr

from shapely.geometry import Polygon, MultiPolygon 
from fiona.crs import from_epsg
import geopandas as gp

#=============================================================================#
# PREAMBLE AND PATH DEFINITIONS
#=============================================================================#
CDLPath= '../../Data/CDL/'
GCAMPath= '../../Data/GCAM/'

files = glob.glob(CDLPath+'cdl*.txt') 


class CdlDataStruct:
    """TODO:  need description of class

    """
    # Constructor requires the path and file name of the input CDL data
    def __init__(self, cdl_path, cdl_infile):
        self.cdl_path   = cdl_path
        self.cdl_infile = cdl_infile
        
    # Add CDL geographic transformation adn projection information
    def SetCDL_ProjInfo(self, GeoTransform, Projection, PixelSize):
        self.cdl_geotransform = GeoTransform
        self.cdl_projection   = Projection
        self.cdl_pixelsize    = PixelSize

    def SetCDLGrid(self,cdl_grid): # Original CDL grid
        self.cdl_grid = cdl_grid

    def SetCDLStats(self,cdl_stats): # Add CDL stats
        self.cdl_stats = cdl_stats


class GCAM_DataStruct:
    def __init__(self, gcam_path, gcam_outfile):
        self.gcam_path    = gcam_path
        self.gcam_outfile = gcam_outfile

    def SetGCAM_ProjInfo(self,GeoTransform,Projection,PixelSize):
        self.gcam_geotransform = GeoTransform
        self.gcam_projection   = Projection
        self.gcam_pixelsize    = PixelSize
        
    def SetGCAMStats(self,gcam_stats): # Add GCAM stats
        self.gcam_stats = gcam_stats

    def SetGCAMGrid(self,gcam_grid): # Add reclassified GCAM grid
        self.gcam_grid = gcam_grid
        
#=============================================================================#
# FUNCTION DEFINITIONS  
#=============================================================================#       
def ReadArcGrid(CDL_struct):
    
    # Construct the full name of the CDL input ArcGrid file
    cdl_file = CDL_struct.cdl_path+'/'+CDL_struct.cdl_infile
    
    # Open the CDL input file using GDAL
    CDL_gdal = gdal.Open(cdl_file)
    CDL_struct.SetCDL_ProjInfo(CDL_gdal.GetGeoTransform(),CDL_gdal.GetProjection(),CDL_gdal.GetGeoTransform()[1])

    cdl_grid = np.float64(CDL_gdal.ReadAsArray())
    cdl_grid[cdl_grid==-9999] = np.nan
    CDL_struct.SetCDLGrid(cdl_grid)

    # Close GDAL CDL dataset to save memory
    CDL_gdal = None
    
    return

def CDL2GCAM(CDL_struct,CDL_cat,GCAM_struct,GCAM_cat):

    cdl_stats  = np.zeros(132)
    gcam_stats = np.zeros(28)
     
    gcam_grid = np.nan*np.ones(CDL_struct.cdl_grid.shape) #new blank np array
    for i in np.arange(CDL_cat.size): #unique cdl categories
        indx,indy = np.where(CDL_struct.cdl_grid == CDL_cat[i])
        gcam_grid[indx,indy] = GCAM_cat[i]
        cdl_stats[i]=indx.size
       
    for i in np.arange(28): # #count of each gcam category
        indx,indy = np.where(gcam_grid == i+1)
        gcam_stats[i] = indx.size  
    
    CDL_struct.SetCDLStats(cdl_stats)
    
    GCAM_struct.SetGCAM_ProjInfo(CDL_struct.cdl_geotransform,CDL_struct.cdl_projection,CDL_struct.cdl_pixelsize)
    GCAM_struct.SetGCAMStats(gcam_stats)
    GCAM_struct.SetGCAMGrid(gcam_grid)
    
    return

def saveGCAMGrid(GCAM_struct):

    gcam_grid = GCAM_struct.gcam_grid
    nrows,ncols = np.shape(gcam_grid) 
    
    gcam_outfile = GCAM_struct.gcam_path + GCAM_struct.gcam_outfile
    
    gcam_driver = gdal.GetDriverByName('Gtiff')
    gcam_gdal   = gcam_driver.Create(gcam_outfile, ncols, nrows, 1, gdal.GDT_Float32)

    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326) # Needed as an intermediate because no inital projection defined 
    gcam_gdal.SetProjection(proj.ExportToWkt())
    gcam_gdal.SetGeoTransform(GCAM_struct.gcam_geotransform)
    gcam_gdal.GetRasterBand(1).WriteArray(GCAM_struct.gcam_grid)
    gdal.Warp(gcam_outfile,gcam_gdal,dstSRS='EPSG:32611')
    
    gcam_gdal.FlushCache()
    gcam_gdal = None

    return

#Complilation of above functions to do conversion 
def c2g(CDL_GCAM_keyfile, conversionID):
    #=========================================================================#
    # 0. Read in category data and create vectors                             #
    #=========================================================================#
    CDL2GCAM_key = pd.read_csv(CDL_GCAM_keyfile, sep=',')
    CDL_cat      = CDL2GCAM_key['CDL_id'].values
    GCAM_cat     = CDL2GCAM_key[conversionID].values #'local_GCAM_id' or set to 'GCAM_id' for regular GCAM categories, or edit the original file to user defineted categories

    #=========================================================================#
    # 1. Initialize a list of CDL structures for analysis                     #
    #=========================================================================#
    CDL_Data  = []
    GCAM_Data = []
    for file in files:
        # Initialize CDL data structures with paths and file names
        cdl_path   = os.path.dirname(file)
        cdl_infile = os.path.basename(file)
        CDL_Data.append(CdlDataStruct(cdl_path,cdl_infile))

        # Initialize GCAM data structures with paths and file names
        gcam_path    = GCAMPath
        gcam_outfile = cdl_infile.replace('cdl','gcam')
        gcam_outfile = gcam_outfile.replace('txt','tiff')
        GCAM_Data.append(GCAM_DataStruct(gcam_path,gcam_outfile)) 
    
    #=========================================================================#
    # 2a. Read in all the CDL files and store data in CDL_DataStruct          #
    #=========================================================================#
    Parallel(n_jobs=6, verbose=60, backend='threading')(delayed(ReadArcGrid)(CDL_Data[i]) \
             for i in np.arange(len(CDL_Data)))

    #=========================================================================#
    # 2b. Perform the CDL-GCAM category conversion                            #
    #=========================================================================#
    Parallel(n_jobs=6, verbose=10, backend='threading')(delayed(CDL2GCAM)(CDL_Data[i],CDL_cat,GCAM_Data[i],GCAM_cat) \
             for i in np.arange(len(CDL_Data))) 

    #=========================================================================#
    # 2c. Save recategorized GCAM grids to files                              #
    #=========================================================================#
    Parallel(n_jobs=6, verbose=30, backend='threading')(delayed(saveGCAMGrid)(GCAM_Data[i]) \
             for i in np.arange(len(CDL_Data))) 

    #=========================================================================#
    # 3. Create Arrays of Results
    #=========================================================================#
    f=len(files)
    CDL_stats  = np.zeros((132,f))
    GCAM_stats = np.zeros((28, f))
    
    for i in np.arange(f):
        CDL_stats[:,i]= CDL_Data[i].cdl_stats
        GCAM_stats[:,i]= GCAM_Data[i].gcam_stats
    np.savetxt(GCAMPath+"cdl_initial.csv", CDL_stats, delimiter=",")
    np.savetxt(GCAMPath+"gcam_initial.csv", GCAM_stats, delimiter=",")
    
#=============================================================================#
# Aggregate to scale of interest
#=============================================================================#
    
def AggregateGCAMGrid(GCAM_ReadWriteDir,GCAM_ReadFile, AggRes):
    
    # Open the GeoTiff based on the input path and file
    src_ds = gdal.Open(GCAM_ReadWriteDir+GCAM_ReadFile)

    # Create the name of the output file by modifying the input file
    GCAM_WriteFile = GCAM_ReadFile.replace('domain','domain'+'_'+str(int(AggRes)))

    # Get key info on the source dataset    
    src_ncols = src_ds.RasterXSize
    src_nrows = src_ds.RasterYSize
    
    src_geot = src_ds.GetGeoTransform()
    src_proj = src_ds.GetProjection()
    src_res  = src_ds.GetGeoTransform()[1]

    agg_factor = AggRes / src_res

    dst_ncols = (int)(src_ncols/agg_factor)
    dst_nrows = (int)(src_nrows/agg_factor)

    dst_driver = gdal.GetDriverByName('Gtiff')
    dst_ds = dst_driver.Create(GCAM_ReadWriteDir+GCAM_WriteFile, dst_ncols, dst_nrows, 1, gdal.GDT_Float32)

    dst_geot = (src_geot[0], src_geot[1]*agg_factor, src_geot[2], src_geot[3], src_geot[4], src_geot[5]*agg_factor)

    dst_ds.SetGeoTransform(dst_geot)
    dst_ds.SetProjection(src_proj)

    gdal.ReprojectImage(src_ds, dst_ds, src_proj, src_proj, gdal.GRA_Mode)

    src_ds = None
    dst_ds = None

    return

#=============================================================================#
# Run aggregation function in parallel
#=============================================================================#

def aggGCAM(AggRes, GCAM_Dir):
    GCAM_ReadFiles = glob.glob(GCAM_Dir +'gcam*domain.tiff')
    
    Parallel(n_jobs=4, verbose=60, backend='threading')(delayed(AggregateGCAMGrid)(GCAM_Dir,os.path.basename(file),AggRes) \
             for file in GCAM_ReadFiles)
    
#----------------------------------------------------------------------------
# Create a set of polygons for entire domain
#----------------------------------------------------------------------------

def grid2poly(year, scale, GCAMpath, DataPath):
    grid_file=GCAMpath+'gcam_'+str(int(year))+'_domain_'+str(int(scale))+'.tiff'
    OutFileName= 'domain_poly_'+str(int(scale))+'.shp'
    
    src= gdal.Open(grid_file)
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
