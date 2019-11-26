#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22, 2019

@author: Kendra Kaiser

Read in GCAMland output, convert to categories used in this instance for profit signal generation
"""

import numpy as np
import sys
import pandas as pd
from scipy.stats import linregress


def main(argv):
    """Description

    :param argv: Array of 5 command line arguments passed from the __main__ function
    :param argv[0]: Name of this function (convert_gcamland_prices)
    :param argv[1]: Number of crops to create profit time series for
    :param argv[2]: Number of time steps in the time series
    :param argv[3]: Name of CSV file with GCAMland outputs including path if CSV file is in a different directory
    :param argv[4]: Name of CSV file to which profit time series will be written, including path to output if in
    a different directory than the script
    :param argv[5]: Start year of model run
    :param argv[6]: Name of key file including path if not in directory
    :param argv[7]: Resolution of model in km
    :return: null (output written to file)
    """

    if len(argv) != 7:
        print('\nERROR: Incorrect number of command line arguments\n')
        print('Usage: convert_gcamland_prices.py <no. crops> <no. time steps> <Input CSV file> <Output CSV file> <Key file>\n')
        print('\tconvert_gcamland_prices.py   = Name of this python script')
        print('\t<no. crops>                  = Number of crops to synthesize prices for')
        print('\t<no. time steps>             = Number of time steps to generate prices for')
        print('\t<CSV file>                   = CSV file containing crop information')
        print('\t                               (see documentation)')
        print('\t<Output CSV file>            = CSV file in which to save output prices')
        print('\t<start year                  = Year that Janus is initiated')
        print('\t<Key file>                   = Key file that contains conversions between GCAM and janus\n')
        sys.exit()

    nc = int(argv[1])
    nt = int(argv[2])
    CropFileIn = argv[3]
    CropFileOut = argv[4]
    year = argv[5]
    key_file = argv[6]
    res = argv[7]

    # Error traps
    assert nc > 0, 'convert_gcamland_prices.py ERROR: Negative number of crops encountered'
    assert nt > 0, 'convert_gcamland_prices.py ERROR: Negative number of time steps encountered'
    assert nc <= 28, 'convert_gcamland_prices.py ERROR: Too many crops encountered'

    # function to find nearest value
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    # read input data
    gcam_dat = pd.read_csv(CropFileIn)
    key = pd.read_csv(key_file)

    # parse input data
    crop_names = gcam_dat.name.unique()
    valid_crops = np.where(key['GCAM_price_id'].notna())  # SRB LU categories with crop prices
    gcam_srb_names = key['GCAM_price_id'][valid_crops[0]]  # crop categories from GCAMland to use for SRB crop prices
    srb_ids = key['local_GCAM_id_list'][valid_crops[0]]

    assert all(np.sort(gcam_srb_names.unique()) == np.sort(crop_names)), 'convert_gcamland_prices.py ERROR: Crop ' \
                                                                         'names from GCAMland do not match keyfile'

    # find start and end years from gcam data
    int_yrs = np.where(gcam_dat['year'] == year)
    end_yrs = np.where(gcam_dat['year'] == find_nearest(gcam_dat['year'], (year + nt)))

    # setup output array
    out = np.zeros([nt + 1, len(valid_crops[0])])
    out[0, :] = np.transpose(srb_ids)

    for c in np.arange(len(crop_names)):
        yrs = gcam_dat['year'][np.arange(int_yrs[0][c], end_yrs[0][c] + 1)]
        yrs_ser = np.arange(yrs.iloc[0], yrs.iloc[-1])
        gcam_dat['value'] = gcam_dat['expectedPrice']*gcam_dat['expectedYield']*247.2*907.185
        prices = gcam_dat['value'][np.arange(int_yrs[0][c], end_yrs[0][c] + 1)]
        # create regression based off of GCAM data
        m, b, r_val, p_val, stderr = linregress(yrs, prices)
        # predict prices for every year
        price_pred = m * yrs_ser + b
        # find corresponding SRB crop to place prices in outfile
        gcam_srb_idx = np.where(gcam_srb_names == crop_names[c])
        for i in np.arange(len(gcam_srb_idx[0])):
            out[1:, gcam_srb_idx[0][i]] = np.transpose(price_pred)

    if out.shape[1] != nc:
        print('\nERROR: Mismatch in number of crops read and provided as input\n')
        print(str(nc) + ' crops were expected, ' + str(out.shape[1]) + ' were read. Check key file\n')
        sys.exit()
    # TODO: fix the warning here
    with open(CropFileOut, 'w') as fp:
        np.savetxt(fp, out, delimiter=',', fmt='%.2f')
        fp.close()


if __name__ == "__main__":
    main(sys.argv)
