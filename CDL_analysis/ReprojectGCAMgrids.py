#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:19:46 2018

@author: lejoflores
"""


import gdal
#import numpy as np
import matplotlib.pyplot as plt
#import os
#from pyproj import Proj

GDAL_res = 3.0 # In units of destination projection

#=============================================================================#
# Set master working  directories                                             #
#=============================================================================#
# Base user directories
lejo_test = '/Users/lejoflores/IM3-BoiseState/CDL_analysis/'
#kendra_test = '/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis/'

user = lejo_test
#user = kendra_test

# Specific directories of where to find the data
# GCAM_GridDir = 'D:\Dropbox\BSU\Python\Data\GCAM_SRP'
GCAM_GridDir  = user + 'GCAM_SRP/'
GCAM_GridFile = 'gcam_2010_srb.tiff'

# Location and name of output file
GCAM_AggWriteDir  = GCAM_GridDir+'3km/'
GCAM_AggWriteFile = 'test_3km.tiff'

#=============================================================================#
# 1. Open source dataset and get geographic information                       #
#=============================================================================#

src_ds = gdal.Open(GCAM_GridDir+GCAM_GridFile)

src_geot = src_ds.GetGeoTransform()
src_proj = src_ds.GetProjection()
src_res  = src_ds.GetGeoTransform()[1]

#Trying to just set projection w gdal
# gdal.Warp(GCAM_AggWriteDir+GCAM_AggWriteFile, src_ds, dstSRS='EPSG:32611')

#=============================================================================#
# 2. Reproject from geographic to UTM                                         #
#=============================================================================#
src_ncols = src_ds.RasterXSize
src_nrows = src_ds.RasterYSize

dst_utm_ncols = src_ncols
dst_utm_nrows = src_ncols

dst_utm_driver = gdal.GetDriverByName('Gtiff')

dst_utm_ds = dst_utm_driver.Create(GCAM_AggWriteDir+GCAM_AggWriteFile, dst_utm_ncols, dst_utm_nrows, 1, gdal.GDT_Float32)


#dst_geot = (src_geot[0], src_geot[1]*agg_factor, src_geot[2], src_geot[3], src_geot[4], src_geot[5]*agg_factor)
#dst_proj = src_proj

#dst_ds.SetGeoTransform(dst_geot)
#dst_ds.SetProjection(dst_proj)




#gdal.ReprojectImage(src_ds, dst_ds, src_proj, dst_proj, gdal.GRA_Mode)



#agg_factor = GDAL_res / src_res




#warping = gdal.WarpOptions(format='Gtiff', xRes=GDAL_res, yRes=GDAL_res, srcSRS=dst_proj, resampleAlg=gdal.GRA_Mode)

#gdal.Warp(GCAM_AggWriteDir+GCAM_AggWriteFile, src_ds, warpOptions=warping)
#
#dst_ds = None
#
#src_ds = None
##
#
#ds   = gdal.Open(GCAM_AggWriteDir+GCAM_AggWriteFile)
#grid = ds.ReadAsArray()
#
#plt.figure(dpi=150)
#plt.imshow(grid)
