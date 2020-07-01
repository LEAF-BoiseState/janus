#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22, 2019

@author: Kendra Kaiser

Read in GCAM-USA output, convert to categories used in this instance for profit signal generation
"""

import numpy as np
import sys
import pandas as pd
from scipy.stats import linregress


def gcam_usa_price_converter(gcam_profits, profits_out, key_file, nc, nt, year):
    """Convert GCAM USA prices to the crop categories defined in the key file and format to be used by Janus

    :param gcam_profits:    Full path and file name to GCAM-USA outputs
    :type gcam_profits:     String
    :param profits_out:     Full path and output file name to CSV file to which profit time series will be written
    :type profits_out:      String
    :param key_file:        Full path and file name of key file
    :type key_file:         String
    :param nc:              Number of crops to create profit time series for
    :type nc:               Integer
    :param nt:              Number of time steps in the time series
    :type nt:               Integer
    :param year:            Start year of model run
    :type year:             Integer

    :return:                null (output written to file)
    """

    # Error traps
    assert nc > 0, 'convert_gcam_usa_prices.py ERROR: Negative number of crops encountered'
    assert nt > 0, 'convert_gcam_usa_prices.py ERROR: Negative number of time steps encountered'
    assert nc <= 28, 'convert_gcam_usa_prices.py ERROR: Too many crops encountered'

    # function to find nearest value
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    # read input data
    gcam_dat = pd.read_csv(gcam_profits)
    key = pd.read_csv(key_file)

    # parse input data
    crop_names = gcam_dat.sector.unique()
    valid_crops = np.where(key['GCAM_USA_price_id'].notna())  # GCAM-USA LU categories with crop prices
    gcam_usa_names = key['GCAM_USA_price_id'][
        valid_crops[0]]  # crop categories from GCAM-USA to use for SRB crop prices
    srb_ids = key['local_GCAM_id_list'][valid_crops[0]]

    # TODO fix this assert, need to drop crops that aren't in the SRB
    #assert all(np.sort(gcam_usa_names.unique()) == np.sort(crop_names)), 'convert_gcam_usa_prices.py ERROR: Crop ' \
                                                                         #'names from gcam_usa do not match keyfile'

    # find start and end years from gcam data
    int_col = np.where(gcam_dat.columns == str(year))[0][0]
    end_yr = find_nearest(gcam_dat.columns[3:-1].astype(int), (year + nt))
    end_col = np.where(gcam_dat.columns == str(end_yr))[0][0]

    # setup output array
    out = np.zeros([nt + 1, len(valid_crops[0])])
    out[0, :] = np.transpose(srb_ids)

    yrs = np.array(gcam_dat.columns[int_col: end_col + 1].astype(int))
    intval = yrs[1] - yrs[0]  # interval between predicted prices
    prices_usa = gcam_dat[gcam_dat['region'] == 'USA']
    prices = prices_usa.iloc[:, int_col:(end_col + 1)]

    # Create linear regressions between each timestep
    for c in np.arange(len(crop_names)):
        for y in np.arange(len(yrs)-1):
            yrs_ser = np.arange(yrs[y], yrs[y]+intval)
            x = [yrs[y], (yrs[y] + intval)]
            # create regression between years of GCAM data
            m, b, r_val, p_val, stderr = linregress(x, prices.iloc[c, y: y+2])
            # predict prices for every year
            price_pred = m * yrs_ser + b
            if y == 0:
                price_ts = price_pred
            else:
                price_ts = np.append(price_ts, price_pred)

        # find corresponding SRB crop to place prices in outfile
        gcam_srb_idx = np.where(gcam_usa_names == crop_names[c])[0]
        for i in np.arange(len(gcam_srb_idx)):
            out[1:, gcam_srb_idx[i]] = np.transpose(price_ts)

    if out.shape[1] != nc:
        print('\nERROR: Mismatch in number of crops read and provided as input\n')
        print(str(nc) + ' crops were expected, ' + str(out.shape[1]) + ' were read. Check key file\n')
        sys.exit()

    # TODO: fix the warning here
    with open(profits_out, 'w') as fp:
        np.savetxt(fp, out, delimiter=',', fmt='%.5f')
        fp.close()
