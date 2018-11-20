#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:19:46 2018

@author: lejoflores & Kendra Kaiser
"""

import gdal
import matplotlib.pyplot as plt

GDAL_res = 0.3

#user = '/Users/lejoflores/'
user = '/Users/kek25/Documents/GitRepos/'

#GCAM_GridDir = 'D:\Dropbox\BSU\Python\Data\GCAM_SRP'
GCAM_GridDir = '/Users/kek25/Dropbox/BSU/Python/Data-IM3/GCAM_SRP/'
#GCAM_GridDir  = user + 'IM3-BoiseState/CDL_analysis/GCAM_SRP/'
GCAM_GridFile = 'gcam_2010_srb.tiff'

GCAM_AggWriteDir  = GCAM_GridDir+'3km/'
GCAM_AggWriteFile = 'test_3km.tiff'

src_ds = gdal.Open(GCAM_GridDir+GCAM_GridFile)

src_geot = src_ds.GetGeoTransform()
src_res  = src_ds.GetGeoTransform()[1]
src_proj = 'epsg:4327' ## - geographic 3D WGS 84 http://spatialreference.org/ref/epsg/4327/

###This is just using warp to project the data - takes 11s -- could be not right because not setting source projection
### that might be the utility of reproject
gdal.Warp(GCAM_AggWriteDir+GCAM_AggWriteFile, src_ds, dstSRS= 'epsg:32611')


ds   = gdal.Open(GCAM_AggWriteDir+GCAM_AggWriteFile)
grid = ds.ReadAsArray()
ds.GetProjection() #projection works... but doesnt change the cell size?

plt.figure(dpi=150) #save works
plt.imshow(grid)


#------
#agg_factor= GDAL_res/ src_res
agg_factor = 1000 
# if the current resolution is 30m and we want 3km  - is that right? 
#seems strange that after being projected the cell size stays at 0.0003? thats in Arc units of degrees

src_ncols = src_ds.RasterXSize
src_nrows = src_ds.RasterYSize

dst_ncols = (int)(src_ncols/agg_factor)
dst_nrows = (int)(src_nrows/agg_factor)


dst_geot = (src_geot[0], src_geot[1]*agg_factor, src_geot[2], src_geot[3], src_geot[4], src_geot[5]*agg_factor)

dst_driver = gdal.GetDriverByName('Gtiff')
dst_ds = dst_driver.Create(GCAM_AggWriteDir+GCAM_AggWriteFile, dst_ncols, dst_nrows, 1, gdal.GDT_Float32)
dst_ds.SetGeoTransform(dst_geot)
dst_proj = 'EPSG:32611' #WGS 84 Zone 11N
dst_ds.SetProjection(dst_proj)

warping = gdal.WarpOptions(format='Gtiff', xRes=GDAL_res, yRes=GDAL_res, dstSRS= dst_proj, resampleAlg=gdal.GRA_Mode)

#this doesn't throw any errors, but when you import it again its one big color
gdal.Warp(GCAM_AggWriteDir+GCAM_AggWriteFile, src_ds, warpOptions=warping)
#gdal.ReprojectImage(src_ds, dst_ds, src_proj, dst_proj, gdal.GRA_Mode)
#### ----- Try this again with the WGS projection
gdal.ReprojectImage(src_ds, dst_ds, src_proj, dst_proj, gdal.GRA_Mode)


dst_ds = None

src_ds = None
#

ds   = gdal.Open(GCAM_AggWriteDir+GCAM_AggWriteFile)
grid = ds.ReadAsArray()

plt.figure(dpi=150)
plt.imshow(grid)
plt.title('BOOM Shakalaka Mothafucka!')