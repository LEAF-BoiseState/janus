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
    def __init__(self,cdl_path,cdl_infile): # We initialize the class only with a filename
        self.cdl_path   = cdl_path
        self.cdl_infile = cdl_infile
        
    def AddCDL_GDALstruct(self,gdal_obj): # A placeholder to add the actual GDAL object
        self.gdal_obj = gdal_obj

    def AddCDLData(self,cdl_grid): # Original CDL grid
        self.cdl_grid = cdl_grid

    def AddCDLStats(self,cdl_stats): # Add CDL stats
        self.cdl_stats = cdl_stats
                
class GCAM_DataStruct:
    def __init__(self,gcam_path,gcam_outfile):
        self.gcam_path    = gcam_path
        self.gcam_outfile = gcam_outfile

    def AddGCAMStats(self,gcam_stats): # Add GCAM stats
        self.gcam_stats = gcam_stats

    def AddGCAMGrid(self,gcam_grid): # Add reclassified GCAM grid
        self.gcam_grid = gcam_grid

    def AddAggregatedGrid(self,agg_grid):
        self.agg_grid = agg_grid

    def AddAggregateStats(self, agg_stats):
        self.agg_stats=agg_stats

#class AggGrid:
#    def __init__(self):
        
#=============================================================================#
# FUNCTION DEFINITIONS    
def ReadArcGrid(CDL_struct):
    
    cdl_file = CDL_struct.cdl_path+'/'+CDL_struct.cdl_infile
    
    gdfid = gdal.Open(cdl_file)

    CDL_struct.AddCDL_GDALstruct(gdfid)

    cdl_grid = np.float64(gdfid.ReadAsArray())
    cdl_grid[cdl_grid==-9999] = np.nan
    
    CDL_struct.AddCDLData(cdl_grid)
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
    
    
    CDL_struct.AddCDLStats(cdl_stats)
    
    
    CDL_struct.AddGCAMStats(gcam_stats)
    CDL_struct.AddGCAMGrid(gcam_grid)
    
    return

def saveGrid(CDL_struct):

    indata = CDL_struct.cdl_grid
    nrows,ncols = np.shape(indata) 

    # Create new file name
    newfn = filename.split('\\')[-1]
    newfn = filename.replace('txt','tiff')
    newfn = filename.replace('cdl','gcam')
    CDL_struct.AddGCAMFileName(GCAM_WriteDir+newfn)
    
    driver  = gdal.GetDriverByName('Gtiff')
    outdata = driver.Create(newfn, ncols, nrows, 1, gdal.GDT_Float32)
    outdata.SetGeoTransform(gdfid.GetGeoTransform())
    outdata.SetProjection(gdfid.GetProjection())
    outdata.GetRasterBand(1).WriteArray(CDL_struct.gcam_grid)
    outdata.FlushCache()
    outdata = None

def warpGrid(CDL_struct,Agg_WriteDir,gdal_res):
    
    gdal_obj      = CDL_struct.gdal_obj
    gcam_grid     = CDL_struct.gcam_grid
    
    gcam_proj     = gdal_obj.GetProjection()
    gcam_geotrans = gdal_obj.GetGeoTransform()
    pixelSizeX    = gdal_obj.GetGeoTransform()[1] #original pixel size
    
    gcamAgg_filename = CDL_struct.filename
    gcamAgg_filename = gcamAgg_filename.replace('cdl','gcam')
    gcamAgg_filename = gcamAgg_filename.replace('txt','tiff')
    warpDir = Agg_WriteDir
    newFile = warpDir+gcamAgg_filename
    
    warping = gdal.WarpOptions(format='Gtiff', xRes=gdal_res, yRes=gdal_res, srcSRS=gcam_proj, resampleAlg='mode')
    gdal.Warp(newFile, gdal_obj, warpOptions=warping)

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
# 2. Read in all the CDL files and store data in CDL_DataStruct               #
#=============================================================================#
Parallel(n_jobs=6, verbose=60, backend='threading')(delayed(ReadArcGrid)(CDL_Data[i]) \
         for i in np.arange(len(CDL_Data)))

#=============================================================================#
# 3. Perform the CDL-GCAM category conversion                                     #
#=============================================================================#
Parallel(n_jobs=6, verbose=10, backend='threading')(delayed(CDL2GCAM)(CDL_Data[i],CDL_cat,GCAM_Data[i],GCAM_cat) \
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
    base_yeild[i]=np.average(np.multiply(perc[pd.notnull(price)], yeild[pd.notnull(price)]))

np.savetxt("base_price.csv", base_price, delimiter=",")
np.savetxt("base_yield.csv",  base_yeild, delimiter=",")

#=============================================================================#
# 6. Save new grids with GCAM categories, aggregate, and save counts
#=============================================================================#

AggregateResolution = 0.01
AggregateResolution3 = 0.03

for i in np.arange(len(CDL_Data)):
    saveGrid(CDL_Data[i])
    warpGrid(CDL_Data[i],Agg_WriteDir,AggregateResolution)
    warpGrid(CDL_Data[i],Agg_WriteDir3,AggregateResolution3)

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
