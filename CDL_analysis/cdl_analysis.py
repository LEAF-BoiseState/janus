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


#os.chdir("/Users/kek25/Dropbox/BSU/Python/Data/")
CDL_GCAM_keyfile = '~/Dropbox/BSU/Python/Data/CDL2GCAM_SRP.csv'

#os.chdir("D:/Dropbox/BSU/Python/Data/CDL")
os.chdir("/Users/kek25/Dropbox/BSU/Python/Data/CDL")
files = glob.glob('*.txt')

#=============================================================================#
# CLASS DEFINITIONS    
class CDL_DataStruct:
    def __init__(self,filename): # We initialize the class only with a filename
        self.filename = filename
    def AddCDLData(self,cdl_grid): # Original CDL grid
        self.cdl_grid = cdl_grid
    def AddCDLStats(self,cdl_stats): # Add CDL stats
        self.cdl_stats = cdl_stats
    def AddGCAMStats(self,gcam_stats): # Add GCAM stats
        self.gcam_stats = gcam_stats
    def AddGCAMGrid(self,gcam_grid): # Add reclassified GCAM grid
        self.gcam_grid = gcam_grid
        
#=============================================================================#
# FUNCTION DEFINITIONS    
def ReadArcGrid(CDL_struct):
    gdfid = gdal.Open(CDL_struct.filename)
    cdl_grid = np.float64(gdfid.ReadAsArray())
    cdl_grid[cdl_grid==-9999] = np.nan
    
    CDL_struct.AddCDLData(cdl_grid)
    
    return

def CDL2GCAM(CDL_struct,CDL_cat,GCAM_cat):

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

#=============================================================================#
# 0. Read in category data and create vectors                                 #
#=============================================================================#
CDL2GCAM_key = pd.read_csv(CDL_GCAM_keyfile, sep=',')
CDL_cat      = CDL2GCAM_key['CDL_id'].values
GCAM_cat     = CDL2GCAM_key['SRP_GCAM_id'].values

#=============================================================================#
# 1. Initialize a list of CDL structures for analysis                         #
#=============================================================================#
CDL_Data = []
for file in files:
   CDL_Data.append(CDL_DataStruct(file))

#=============================================================================#
# 2. Read in all the CDL files and store data in CDL_DataStruct               #
#=============================================================================#
Parallel(n_jobs=6, verbose=60, backend='threading')(delayed(ReadArcGrid)(CDL_Data[i]) \
         for i in np.arange(len(CDL_Data)))

#=============================================================================#
# 3. Perform the CDL-GCAM data analysis                                       #
#=============================================================================#
Parallel(n_jobs=6, verbose=10, backend='threading')(delayed(CDL2GCAM)(CDL_Data[i],CDL_cat,GCAM_cat) \
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
# 6. Save new grids with GCAM categories
#=============================================================================#
os.chdir("D:/Dropbox/BSU/Python/Data/CDL")

def saveGrid(CDL_struct):
    filename = CDL_struct.filename
    gdfid = gdal.Open(filename)
    indata = CDL_struct.cdl_grid

    nrows,ncols = np.shape(indata) 

    os.chdir("D:/Dropbox/BSU/Python/Data/CDL_GCAM_SRP")
    newfn =filename.split(".",-1)[0] + ".tiff"
    driver = gdal.GetDriverByName('Gtiff')
    outdata= driver.Create(newfn, ncols, nrows, 1, gdal.GDT_Float32)
    outdata.SetGeoTransform(gdfid.GetGeoTransform())
    outdata.SetProjection(gdfid.GetProjection())
    outdata.GetRasterBand(1).WriteArray(CDL_Data[i].gcam_grid)

    outdata.FlushCache()
    outdata = None

#im not sure about the class structure - so I don't think this is correct ...
for i in np.arange(len(CDL_data)):
    saveGrid(CDL_DataStruct[i])
    

#tst =gdal.Open("D:/Dropbox/BSU/Python/Data/CDL_GCAM_SRP/cdl_2010_srb.tiff")
#tst_grid = np.float64(tst.ReadAsArray())
#tst_grid[tst ==-9999] = np.nan   
#plt.imshow(tst)

#=============================================================================#
# 7. Create new grids at lower resolution (1km)
#=============================================================================#
os.chdir("D:/Dropbox/BSU/Python/Data/CDL_GCAM_SRP")
#os.chdir("/Users/kek25/Dropbox/BSU/Python/Data/CDL_GCAM_SRP")

src = gdal.Open("cdl_2010_srb.tiff")
cdl_grid = np.float64(src.ReadAsArray())

src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()

pixelSizeX=src.GetGeoTransform()[1] #original pixel size

warpDir="D:/Dropbox/BSU/Python/Data/CDL_GCAM_SRP/1km/"
newFile= warpDir+"cdl_2010_srb.tiff"
warping = gdal.WarpOptions(format='Gtiff', xRes= 0.01, yRes=0.01, srcSRS=src_proj, resampleAlg='mode')
gdal.Warp(newFile, src, warpOptions=warping)

os.chdir="D:/Dropbox/BSU/Python/Data/CDL_GCAM_SRP/1km/"
src = gdal.Open("cdl_2010_srb.tiff")
cdl_grid = np.float64(src.ReadAsArray())
plt.imshow(cdl_grid)


#how to count categories way better
tst=np.array(cdl_grid).flatten()
tst=tst[pd.notnull(tst)]
m = dict()
for x in tst:
    try:
        m[x] += 1
    except:
        m[x] = 1
print(m)


#=============================================================================#
# 7. Clip out a few counties - Twin, Jerome, Minidoka and Ada/Canyon
#=============================================================================#

from osgeo import ogr
import shapefile

sf = shapefile.Reader("SRB_counties")

layer = reader.GetLayer()
feature = layer.GetFeature(0)
geoms =json.loads(feature.ExportToJson())['geometry']
print geoms
