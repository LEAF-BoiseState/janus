#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 14:23:05 2019

@author: lejoflores
"""


import numpy as np
import sys
import csv

NPRICE_FUNCTIONS = 3


# 0. Get number of crops and number of timesteps from command line input
# 1. Read in a csv file that contains columns corresponding to: (1) crop ID number, (2) crop name,
#    (3) functional behavior, (4) parameters whose number depends on the specific functional 
#    behavior chosen.
#


if(len(sys.argv)!=5):
    print('\nERROR: Incorrect number of command line arguments\n')
    print('Usage: GenerateSyntheticPrices.py <no. crops> <no. timesteps> <CSV file> <Output .npy file>\n')
    print('\tGenerateSyntheticPrices.py = Name of this python script')
    print('\t<no. crops>                = Number of crops to synthesize prices for')
    print('\t<no. timesteps>            = Number of timesteps to generate prices for')
    print('\t<CSV file>                 = CSV file containing crop information')
    print('\t                             (see documentation)')
    print('\t<Output .NPY file>         = NPY filel in which to save output prices\n')
    sys.exit()

Nc       = int(sys.argv[1])
Nt       = int(sys.argv[2])
CropFile = sys.argv[3]

# Error traps
assert Nc > 0, 'GenerateSyntheticPrices.py ERROR: Negative number of crops encountered'
assert Nt > 0, 'GenerateSyntheticPrices.py ERROR: Negative number of timesteps encountered'
assert Nc <= 28, 'GenerateSyntheticPrices.py ERROR: Too many crops encountered'

# Try opening the CSV file provided as input 
try:
    fp = open(CropFile)
except IOError as e:
    print('GenerateSyntheticPrices.py ERROR({0}): {1}'.format(e.errno, e.strerror))
    
csv_fp = csv.reader(fp)

crop_names = []
crop_ids   = []

CropCount = 0

for row in csv_fp:
    
    CropCount += 1

    assert isinstance(row[0],str),'GenerateSyntheticPrices.py ERROR: Crop name not string'
    crop_names.append(row[0])
    
    assert int(row[1])>0,'GenerateSyntheticPrices.py ERROR: Negative crop ID number'
    crop_ids.append(int(row[1]))
    
    assert int(row[2]>0), 'GenerateSyntheticPrices.py ERROR: Invalid price function behavior flag'
    assert int(row[2]<(NPRICE_FUNCTIONS+1)), 'GenerateSyntheticPrices.py ERROR: Invalid price function behavior flag'
    
    price_fxn_type = int(row[2])
    
    if(price_fxn_type==1): # Linear ramp (use for linearlly increasing, decreasing, constant prices)
        assert len(row)==7,'GenerateSyntheticPrices.py ERROR: Incorrect number of parameters in row ' + str(CropCount)
        
        Pi       = float(row[3])
        Pf       = float(row[4])
        perturb  = int(row[5])
        s_p      = float(row[6])
    elif(price_fxn_type==2): # Step function (use for step increase or decrease in price)


        
    elif(price_fxn_type==3): # Sinusoidal fluctuation in price
        
    


def GeneratePrice_linear(Nt,Pi,Pf,perturb,s_p):
    
    P = np.linspace(Pi,Pf,num=Nt).reshape((Nt,1))
    if(perturb==1):
        P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))
    
    return P

def GeneratePrice_step(Nt,Pi,Pf,t_step,perturb,s_p):
    
    assert t_step > 0.0, 'GenerateSyntheticPrices.py ERROR: Step price change time is less than 0.0'
    assert t_step < 1.0, 'GenerateSyntheticPrices.py ERROR: Step price change time is greeater than 1.0'
    
    
    P = np.zeros((Nt,1))
    P[0:(int(t_step*Nt))] = Pi
    P[(int(t_step*Nt)):]  = Pf

    if(perturb==1):
        P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))

    return P

def GeneratePrice_periodic(Nt,Pmag,Pamp,n_period,perturb,s_p):
    

    x = np.linspace(0.0,n_period*2*np.pi, num=Nt).reshape((Nt,1))
    P = Pmag + Pamp  * np.sin(x)
    
    if(perturb==1):
        P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))
      
    return P



