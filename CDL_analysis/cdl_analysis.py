#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 21:47:36 2018

@author: lejoflores and Kendra Kaiser
"""

import gdal
import glob 
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import pandas as pd
import os

#=============================================================================#
# PREAMBLE AND PATH DEFINITIONS
#=============================================================================#

LejoDataPath  = '/Users/lejoflores/Dropbox/CDL/'
LejoWritePath = '/Users/lejoflores/IM3-BoiseState/CDL_analysis/'

#CDL_GCAM_keyfile = '~/Dropbox/BSU/Python/Data/CDL2GCAM_SRP.csv'
CDL_GCAM_keyfile = LejoWritePath+'CDL2GCAM_SRP.csv'

CDL_ReadDir   =  LejoDataPath #'D:/Dropbox/BSU/Python/Data/CDL/'
#CDL_ReadDir  = '/Users/kek25/Dropbox/BSU/Python/Data/CDL/'

GCAM_WriteDir = LejoWritePath+'GCAM_SRP/'
Agg_WriteDir  = LejoWritePath+'GCAM_SRP/1km/'
Agg_WriteDir3 = LejoWritePath+'GCAM_SRP/3km/'

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

    # These should probably go in a separate class ~>
    def AddAggregatedGrid(self,agg_grid):
        self.agg_grid = agg_grid

    def AddAggregateStats(self, agg_stats):
        self.agg_stats=agg_stats

#class AggGrid:
#    def __init__(self):
        
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

    gcam_gdal.SetGeoTransform(GCAM_struct.gcam_geotransform)
    gcam_gdal.SetProjection(GCAM_struct.gcam_projection)
    gcam_gdal.GetRasterBand(1).WriteArray(GCAM_struct.gcam_grid)
    gcam_gdal.FlushCache()
    gcam_gdal = None

    return

def warpGrid(GCAM_struct,Agg_WriteDir,Agg_WriteFile,gdal_res):
    
    gcam_geotransform = GCAM_struct.gcam_geotransform
    gcam_projection   = GCAM_struct.gcam_projection
    gcam_pixelsize    = GCAM_struct.gcam_pixelsize
    gcam_grid         = GCAM_struct.gcam_grid
    
    pixelSizeX    = gdal_obj.GetGeoTransform()[1] #original pixel size
    
    AggFileFull = Agg_WriteDir+Agg_WriteFile
    
    warping = gdal.WarpOptions(format='Gtiff', xRes=gdal_res, yRes=gdal_res, srcSRS=gcam_projection, resampleAlg='mode')
    gdal.Warp(AggFileFull, gdal_obj, warpOptions=warping)

    return
#=============================================================================#
# 0. Read in category data and create vectors                                 #
#=============================================================================#
CDL2GCAM_key = pd.read_csv(CDL_GCAM_keyfile, sep=',')
CDL_cat      = CDL2GCAM_key['CDL_id'].values
GCAM_cat     = CDL2GCAM_key['SRP_GCAM_id'].values

#=============================================================================#
# 1. Initialize a list of CDL structures for analysis                         #
#=============================================================================#
CDL_Data  = []
GCAM_Data = []
for file in files:
    # Initialize CDL data structures with paths adn file names
    cdl_path   = os.path.dirname(file)
    cdl_infile = os.path.basename(file)
    CDL_Data.append(CDL_DataStruct(cdl_path,cdl_infile))

    # Initialize GCAM data structures with paths and file names
    gcam_path    = GCAM_WriteDir
    gcam_outfile = cdl_infile.replace('cdl','gcam')
    gram_outfile = gcam_outfile.replace('txt','tiff')
    GCAM_Data.append(GCAM_DataStruct(gcam_path,gram_outfile)) 
    
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
# 4. Create Arrays of Results
#=============================================================================#
f=len(files)
CDL_stats  = np.zeros((132,f))
GCAM_stats = np.zeros((28, f))
    
for i in np.arange(f):
    CDL_stats[:,i]= CDL_Data[i].cdl_stats
    GCAM_stats[:,i]= CDL_Data[i].gcam_stats

np.savetxt("cdl_res.csv", CDL_stats, delimiter=",")
np.savetxt("gcam_res.csv", GCAM_stats, delimiter=",")

#=============================================================================#
# 5. Calculate area weighted GCM Yeilds and Prices from CDL data
#=============================================================================#
base_area= CDL_stats[:,0]
base_price = np.zeros((28))
base_yeild = np.zeros((28))

for i in np.arange(28):
    price=CDL2GCAM_key['Price'][GCAM_cat == i+1]
    price.astype(float)
    tmp=base_area[GCAM_cat == i+1] 
    area=sum(tmp[pd.notnull(price)])
    perc = np.divide(tmp, area)
    yeild=CDL2GCAM_key['Yeild'][GCAM_cat == i+1]
    
    base_price[i]=np.average(np.multiply(perc[pd.notnull(price)], price[pd.notnull(price)]))

    ## I BEFORE E EXCEPT AFTER C, YO!!!!!! =====> 
    base_yeild[i]=np.average(np.multiply(perc[pd.notnull(price)], yeild[pd.notnull(price)]))

np.savetxt("base_price.csv", base_price, delimiter=",")
np.savetxt("base_yield.csv",  base_yeild, delimiter=",")

#=============================================================================#
# 6. Save new grids with GCAM categories, aggregate, and save counts
#=============================================================================#

AggregateResolution = 0.01
AggregateResolution3 = 0.03

    #warpGrid(CDL_Data[i],Agg_WriteDir,AggregateResolution)
    #warpGrid(CDL_Data[i],Agg_WriteDir3,AggregateResolution3)

#tst =gdal.Open("D:/Dropbox/BSU/Python/Data/CDL_GCAM_SRP/cdl_2010_srb.tiff")
#tst_grid = np.float64(tst.ReadAsArray())
#tst_grid[tst ==-9999] = np.nan   
#plt.imshow(tst)

#=============================================================================#
# 7. Clip out a few counties - Twin, Jerome, Minidoka and Ada/Canyon
#=============================================================================#
#
#from osgeo import ogr
#import shapefile
#
#sf = shapefile.Reader("SRB_counties")
#
#layer = reader.GetLayer()
#feature = layer.GetFeature(0)
#geoms =json.loads(feature.ExportToJson())['geometry']
#print (geoms)
