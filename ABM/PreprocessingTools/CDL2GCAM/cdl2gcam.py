#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

#=============================================================================#
# PREAMBLE AND PATH DEFINITIONS
#=============================================================================#
#update these for the JORS release
DataPath= '/Users/kek25/Dropbox/BSU/Python/IM3/CDL/'#THIS ISN"T RUNNING ON MY DESKTOP
WritePath= '/Users/kek25/Dropbox/BSU/Python/IM3/'

CDL_GCAM_keyfile =DataPath + 'CDL2GCAM_SRP_categories.csv'
CDL_ReadDir  = DataPath
GCAM_WriteDir = WritePath+'GCAM_SRP/'

files = glob.glob(CDL_ReadDir+'cdl*.txt') 

#=============================================================================#
# CLASS DEFINITIONS    
class CDL_DataStruct:
    # Constructor requires the path and file name of the input CDL data
    def __init__(self,cdl_path,cdl_infile): 
        self.cdl_path   = cdl_path
        self.cdl_infile = cdl_infile
        
    # Add CDL geographic transformation adn projection information
    def SetCDL_ProjInfo(self,GeoTransform,Projection,PixelSize):
        self.cdl_geotransform = GeoTransform
        self.cdl_projection   = Projection
        self.cdl_pixelsize    = PixelSize

    def SetCDLGrid(self,cdl_grid): # Original CDL grid
        self.cdl_grid = cdl_grid

    def SetCDLStats(self,cdl_stats): # Add CDL stats
        self.cdl_stats = cdl_stats
                
class GCAM_DataStruct:
    def __init__(self,gcam_path,gcam_outfile):
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
    proj.ImportFromEPSG(4326) # << NEEDED AS AN INTERMEDIATE BECAUSE NO INITIAL PROJECTION DEFINED <<
    gcam_gdal.SetProjection(proj.ExportToWkt())
    gcam_gdal.SetGeoTransform(GCAM_struct.gcam_geotransform)
    gcam_gdal.GetRasterBand(1).WriteArray(GCAM_struct.gcam_grid)
    gdal.Warp(gcam_outfile,gcam_gdal,dstSRS='EPSG:32611')
    
    gcam_gdal.FlushCache()
    gcam_gdal = None

    return

#=============================================================================#
# 0. Read in category data and create vectors                                 #
#=============================================================================#
CDL2GCAM_key = pd.read_csv(CDL_GCAM_keyfile, sep=',')
CDL_cat      = CDL2GCAM_key['CDL_id'].values
GCAM_cat     = CDL2GCAM_key['SRP_GCAM_id'].values #this can be set to GCAM_id for regular GCAM categories, or edit the original file to user defineted categories

#=============================================================================#
# 1. Initialize a list of CDL structures for analysis                         #
#=============================================================================#
CDL_Data  = []
GCAM_Data = []
for file in files:
    # Initialize CDL data structures with paths and file names
    cdl_path   = os.path.dirname(file)
    cdl_infile = os.path.basename(file)
    CDL_Data.append(CDL_DataStruct(cdl_path,cdl_infile))

    # Initialize GCAM data structures with paths and file names
    gcam_path    = GCAM_WriteDir
    gcam_outfile = cdl_infile.replace('cdl','gcam')
    gcam_outfile = gcam_outfile.replace('txt','tiff')
    GCAM_Data.append(GCAM_DataStruct(gcam_path,gcam_outfile)) 
    
#=============================================================================#
# 2a. Read in all the CDL files and store data in CDL_DataStruct              #
#=============================================================================#
Parallel(n_jobs=6, verbose=60, backend='threading')(delayed(ReadArcGrid)(CDL_Data[i]) \
         for i in np.arange(len(CDL_Data)))

#=============================================================================#
# 2b. Perform the CDL-GCAM category conversion                                #
#=============================================================================#
Parallel(n_jobs=6, verbose=10, backend='threading')(delayed(CDL2GCAM)(CDL_Data[i],CDL_cat,GCAM_Data[i],GCAM_cat) \
         for i in np.arange(len(CDL_Data))) 

#=============================================================================#
# 2c. Save recategorized GCAM grids to files                                  #
#=============================================================================#
Parallel(n_jobs=6, verbose=30, backend='threading')(delayed(saveGCAMGrid)(GCAM_Data[i]) \
         for i in np.arange(len(CDL_Data))) 
#=============================================================================#
# 3. Create Arrays of Results - consider deleting
#=============================================================================#
f=len(files)
CDL_stats  = np.zeros((132,f))
GCAM_stats = np.zeros((28, f))
    
for i in np.arange(f):
    CDL_stats[:,i]= CDL_Data[i].cdl_stats
    GCAM_stats[:,i]= GCAM_Data[i].gcam_stats

np.savetxt("cdl_res.csv", CDL_stats, delimiter=",")
np.savetxt("gcam_res.csv", GCAM_stats, delimiter=",")

#=============================================================================#
# 4. Calculate area weighted GCM Yields and Prices from CDL data - delete
#=============================================================================#
base_area= CDL_stats[:,0]
base_price = np.zeros((28))
base_yield = np.zeros((28))

for i in np.arange(28):
    price=CDL2GCAM_key['Price'][GCAM_cat == i+1]
    price.astype(float)
    tmp=base_area[GCAM_cat == i+1] 
    area=sum(tmp[pd.notnull(price)])
    perc = np.divide(tmp, area)
    yieldV=CDL2GCAM_key['Yield'][GCAM_cat == i+1]
    
    base_price[i]=np.average(np.multiply(perc[pd.notnull(price)], price[pd.notnull(price)]))
    base_yield[i]=np.average(np.multiply(perc[pd.notnull(price)], yieldV[pd.notnull(price)]))

np.savetxt("base_price.csv", base_price, delimiter=",")
np.savetxt("base_yield.csv",  base_yield, delimiter=",")
