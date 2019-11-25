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
    :param argv[4]: Name of CSV file to which profit time series will be written, including path to output if in a different directory than the script
    :param argv[5]: Start year of model run
    :param argv[6]: Name of key file including path if not in directory
    :return: null (output written to file)
    """

    if (len(argv) != 7):
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

    Nc = int(argv[1])
    Nt = int(argv[2])
    CropFileIn = argv[3]
    CropFileOut = argv[4]
    year = argv[5]
    key_file = argv[6]

    # Error traps
    assert Nc > 0, 'convert_gcamland_prices.py ERROR: Negative number of crops encountered'
    assert Nt > 0, 'convert_gcamland_prices.py ERROR: Negative number of time steps encountered'
    assert Nc <= 28, 'convert_gcamland_prices.py ERROR: Too many crops encountered'

    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    df = pd.read_csv(CropFileIn)
    key = pd.read_csv(key_file)

    crop_names = df.name.unique()
    crop_ids = key['GCAM_SRB_id'][0:len(crop_names)]
    valid_crops = np.where(key['GCAM_price_id'].notna())

    srb_ids = key['local_GCAM_id_list'][valid_crops[0]]
    gcam_price_ids = key['GCAM_price_id'][valid_crops[0]].astype(int)
    int_yrs = np.where(df['year'] == year)
    end_yrs = np.where(df['year'] == find_nearest(df['year'], (year+Nt)))

    # setup output array
    out = np.zeros([Nt+1, len(valid_crops[0])])
    out[0, :] = np.transpose(srb_ids)

    for c in np.arange(len(crop_names)):
        yrs = df['year'][np.arange(int_yrs[0][c], end_yrs[0][c]+1)]
        yrs_ser = np.arange(yrs.iloc[0], yrs.iloc[-1])
        # TODO: potentially use profit calculated as profit / km2
        prices = df['expectedPrice'][np.arange(int_yrs[0][c], end_yrs[0][c]+1)]
        m, b, r_val, p_val, stderr = linregress(yrs, prices)
        price_pred = m*yrs_ser + b
        conversion = np.where(gcam_price_ids == crop_ids[c])
        out[1:, conversion[0][0]] = np.transpose(price_pred)

    if out.shape[1] != Nc:
        print('\nERROR: Mismatch in number of crops read and provided as input\n')
        print(str(Nc) + ' crops were expected, ' + str(out.shape[1]) + ' were read. Check key file\n')
        sys.exit()

    with open(CropFileOut, 'w') as fp:

        #np.savetxt(fp, np.asarray(crop_ids, dtype=np.int32).reshape((1, Nc)), delimiter=',', fmt='%d')
        np.savetxt(fp, out, delimiter=',', fmt='%.2f')

        fp.close()


if __name__ == "__main__":
    main(sys.argv)