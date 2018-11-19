#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:19:46 2018

@author: lejoflores
"""


import gdal
import numpy as np
import matplotlib.pyplot as plt
import os

GDAL_res = 0.05

GCAM_GridDir  = '/Users/lejoflores/IM3-BoiseState/CDL_analysis/GCAM_SRP/'
GCAM_GridFile = 'gcam_2010_srb.tiff'

GCAM_AggWriteDir  = GCAM_GridDir+'3km/'
GCAM_AggWriteFile = 'test_3km.tiff'

src_ds = gdal.Open(GCAM_GridDir+GCAM_GridFile)

src_geot = src_ds.GetGeoTransform()
src_proj = src_ds.GetProjection()
src_res  = src_ds.GetGeoTransform()[1]

agg_factor = GDAL_res / src_res

src_ncols = src_ds.RasterXSize
src_nrows = src_ds.RasterYSize

dst_ncols = (int)(src_ncols/agg_factor)
dst_nrows = (int)(src_nrows/agg_factor)


dst_driver = gdal.GetDriverByName('Gtiff')

dst_geot = (src_geot[0], src_geot[1]*agg_factor, src_geot[2], src_geot[3], src_geot[4], src_geot[5]*agg_factor)
dst_proj = src_proj

dst_ds = dst_driver.Create(GCAM_AggWriteDir+GCAM_AggWriteFile, dst_ncols, dst_nrows, 1, gdal.GDT_Float32)
dst_ds.SetGeoTransform(dst_geot)
dst_ds.SetProjection(dst_proj)

warping = gdal.WarpOptions(format='Gtiff', xRes=GDAL_res, yRes=GDAL_res, srcSRS=dst_proj, resampleAlg=gdal.GRA_Mode)

#gdal.Warp(GCAM_AggWriteDir+GCAM_AggWriteFile, src_ds, warpOptions=warping)
gdal.ReprojectImage(src_ds, dst_ds, src_proj, dst_proj, gdal.GRA_Mode)

dst_ds = None

src_ds = None
#

ds   = gdal.Open(GCAM_AggWriteDir+GCAM_AggWriteFile)
grid = ds.ReadAsArray()

plt.figure(dpi=150)
plt.imshow(grid)
