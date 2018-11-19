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

GDAL_res = 0.25

GCAM_GridDir  = '/Users/lejoflores/IM3-BoiseState/CDL_analysis/GCAM_SRP/'
GCAM_GridFile = 'gcam_2010_srb.tiff'

GCAM_AggWriteDir  = GCAM_GridDir+'3km/'
GCAM_AggWriteFile = 'test_3km.tiff'

ds = gdal.Open(GCAM_GridDir+GCAM_GridFile)

gcam_projection = ds.GetProjection()


warping = gdal.WarpOptions(format='Gtiff', xRes=GDAL_res, yRes=GDAL_res, srcSRS=gcam_projection, resampleAlg='mode')
gdal.Warp(GCAM_AggWriteDir+GCAM_AggWriteFile, ds, warpOptions=warping)

ds = None

ds = gdal.Open(GCAM_AggWriteDir+GCAM_AggWriteFile)

grid = ds.ReadAsArray()

plt.figure(figsize=(12,10),dpi=300)
plt.imshow(grid)