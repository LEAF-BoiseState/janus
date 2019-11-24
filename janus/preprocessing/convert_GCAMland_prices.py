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

def main(argv):
    """Description

    :param argv: Array of 5 command line arguments passed from the __main__ function
    :param argv[0]: Name of this function (convert_gcamland_prices)
    :param argv[1]: Number of crops expect to create profit time series for
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

    df=pd.read_csv(CropFileIn)
    key = pd.read_csv(key_file)
    crop_names = df.name.unique()
    crop_ids = key['GCAM_SRB_id'][0:len(crop_names)]
    SRB_ids=np.where(key['GCAM_price_id'].notna())

# TODO: this is where im working ...
    for row in csv_fp:

        CropCount += 1

        assert isinstance(row[0], str), 'convert_gcamland_prices.py ERROR: Crop name not string'




        if (CropCount == 1):
            P_allcrops = P
        else:
            P_allcrops = np.column_stack((P_allcrops, P))

    if (CropCount != Nc):
        print('\nERROR: Mismatch in number of crops read and provided as input\n')
        print(str(Nc) + ' crops were expected, ' + str(CropCount) + ' were read. Check input\n')
        sys.exit()

    with open(CropFileOut, 'w') as fp:

        np.savetxt(fp, np.asarray(crop_ids, dtype=np.int32).reshape((1, Nc)), delimiter=',', fmt='%d')
        np.savetxt(fp, P_allcrops, delimiter=',', fmt='%.2f')

        fp.close()


if __name__ == "__main__":
    main(sys.argv)