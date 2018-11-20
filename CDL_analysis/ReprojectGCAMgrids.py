#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:19:46 2018

@author: lejoflores
"""

import gdal
import glob
import os
from joblib import Parallel, delayed

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
GCAM_ReadDir   = user + 'GCAM_SRP/'
GCAM_ReadFiles = glob.glob(GCAM_ReadDir+'gcam*srb.tiff')

# Location and name of output file
GCAM_ReprojWriteDir  = GCAM_ReadDir + 'test_out/'
GCAM_ReprojWriteFile = 'test_utm11N.tiff'

dst_epsg_str = 'EPSG:32611'

#=============================================================================#
# FUNCTION DEFINITIONS    
def ReprojectGCAMGrid(GCAM_ReadDir,GCAM_ReadFile,GCAM_WriteDir,dst_epsg_str):
    
    # Open the GeoTiff based on the input path and file
    src_ds = gdal.Open(GCAM_ReadDir+GCAM_ReadFile)

    # Create the name of the output file by modifying the input file
    GCAM_WriteFile = GCAM_ReadFile.replace('srb','srb_geo')

    # Use gdal.Warp to reproject the file
    gdal.Warp(GCAM_WriteDir+GCAM_WriteFile,src_ds,dstSRS='EPSG:4326') ## << NEEDED AS AN INTERMEDIATE BECAUSE NO INITIAL PROJECTION DEFINED

    src_ds = None
    
    src_ds = gdal.Open(GCAM_WriteDir+GCAM_WriteFile)

    # Create the name of the output file by modifying the input file
    GCAM_WriteFile = GCAM_ReadFile.replace('srb','srb_utm11N')

    # Use gdal.Warp to reproject the file
    gdal.Warp(GCAM_WriteDir+GCAM_WriteFile,src_ds,dstSRS=dst_epsg_str)
    
    # Clean up
    src_ds = None
    
    return

#=============================================================================#
Parallel(n_jobs=6, verbose=60, backend='threading')(delayed(ReprojectGCAMGrid)(GCAM_ReadDir,os.path.basename(file),GCAM_ReprojWriteDir,dst_epsg_str) \
         for file in GCAM_ReadFiles)

