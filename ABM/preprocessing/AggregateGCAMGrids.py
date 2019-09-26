#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 21:33:10 2018

@author: lejoflores and kendrakaiser
"""

import gdal
import glob
import os
from joblib import Parallel, delayed

#=============================================================================#
# FUNCTION DEFINITIONS    
def AggregateGCAMGrid(GCAM_ReadWriteDir,GCAM_ReadFile, AggRes):
    
    # Open the GeoTiff based on the input path and file
    src_ds = gdal.Open(GCAM_ReadWriteDir+GCAM_ReadFile)

    # Create the name of the output file by modifying the input file
    GCAM_WriteFile = GCAM_ReadFile.replace('srb','srb'+'_'+str(int(AggRes)))

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
#                                                                             #
#=============================================================================#

def aggGCAM(AggRes, GCAM_Dir):
    
    GCAM_ReadFiles = glob.glob(GCAM_Dir +'gcam*srb.tiff')

    Parallel(n_jobs=4, verbose=60, backend='threading')(delayed(AggregateGCAMGrid)(GCAM_Dir,os.path.basename(file),AggRes) \
             for file in GCAM_ReadFiles)