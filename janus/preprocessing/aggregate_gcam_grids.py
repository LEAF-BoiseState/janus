"""
Created on Mon Nov 19 21:33:10 2018

@author: lejoflores and kendrakaiser
"""

import glob
import os

import gdal

from joblib import Parallel, delayed


def aggregate_gcam_grid(GCAM_ReadWriteDir,GCAM_ReadFile, AggRes):
    """

    :param GCAM_ReadWriteDir:
    :param GCAM_ReadFile:
    :param AggRes:

    :return:
    
    """
    
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


def aggregate_gcam(AggRes, gcam_directory):
    """

    :param AggRes:
    :param gcam_directory:

    :return:

    """

    gcam_files = glob.glob(os.path.join(gcam_directory, 'gcam*srb.tiff'))

    Parallel(n_jobs=4, verbose=60, backend='threading')(delayed(aggregate_gcam_grid)(gcam_directory,
                                                                                     os.path.basename(file), AggRes)
                                                        for file in gcam_files)
