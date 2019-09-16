#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 14:23:05 2019

@author: lejoflores
"""


import numpy as np
import sys
import csv

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

for row in csv_fp:
    
    assert isinstance(row[0],str),'GenerateSyntheticPrices.py ERROR: Crop name not string'
    crop_names.append(row[0])
    
    assert int(row[1])>0,'GenerateSyntheticPrices.py ERROR: Negative crop ID number'
    crop_ids.append(int(row[1]))
    
    
    

CropCount = 0


def GeneratePrice_linear(Nt,Pi,Pf,s_p):
    
    P = np.linspace(Pi,Pf,num=Nt).reshape((Nt,1)) 
    P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))
    
    return P

def GeneratePrice_step(Nt,Pi,Pf,t_step,s_p):
    
    assert t_step > 0.0, 'GenerateSyntheticPrices.py ERROR: Step price change time is less than 0.0'
    assert t_step < 1.0, 'GenerateSyntheticPrices.py ERROR: Step price change time is greeater than 1.0'
    
    
    P = np.zeros((Nt,1))
    P[0:(int(t_step*Nt))] = Pi
    P[(int(t_step*Nt)):]  = Pf
    P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))

    return P

def GeneratePrice_periodic(Nt,Pmag,Pamp,t_p,s_p):
    
    

    








#
#
##=============================================================================#
##                                                                             #
## GeneratePrices: Generates 6 synthetic crop profits with different           #
##                 behaviors. This function is largely for debugging purposes  #
##                 to test new model test cases, etc.                          #
##                                                                             #
##=============================================================================#
#
#def GeneratePrices(Nt):
#    
#    # Crop 1 = Steadily increasing
#    P1_i = 20000.0
#    P1_f = 31000.0
#    P1_s = 1000.0
#
#    P1 = (np.linspace(P1_i,P1_f,num=Nt).reshape((Nt,1)) + np.random.normal(loc=0.0, scale=P1_s, size=(Nt,1)))
#    
#    # Crop 2
#    P2_i = 30000.0
#    P2_f = 15000.0
#    P2_s = 1000.0
#    
#    P2 = (np.linspace(P2_i,P2_f,num=Nt).reshape((Nt,1)) + np.random.normal(loc=0.0, scale=P2_s, size=(Nt,1)))
#    
#    # Crop 3 = Sinusoidal fluctuation
#    P3_l = 28000.0
#    P3_a = 5000.0
#    P3_n = 2.0
#    P3_s = 1000.0
#    
#    x3 = np.linspace(0.0, P3_n*2*np.pi, num=Nt).reshape((Nt,1))
#    P3 = (P3_l + P3_a*np.sin(x3) + np.random.normal(loc=0.0, scale=P3_s, size=(Nt,1)))
#    
#    # Crop 4 = Step decrease
#    P4_i = 31000.0
#    P4_f = 14000.0
#    P4_s = 1000.0
#    
#    P4 = np.zeros((Nt,1))
#    P4[0:(int(P4.size/2))] = P4_i
#    P4[(int(P4.size/2)):]  = P4_f
#    P4 += np.random.normal(loc=0.0, scale=P4_s, size=(Nt,1))
#    
#    # Crop 5 = Step increase
#    P5_i = 10000.0
#    P5_f = 30000.0
#    P5_s = 1000.0
#
#    P5 = np.zeros((Nt,1))
#    P5[0:(int(P5.size/2))] = P5_i
#    P5[(int(P5.size/2)):]  = P5_f
#    P5 += np.random.normal(loc=0.0, scale=P5_s, size=(Nt,1))
#    
#    # Crop 6 = Constant with noise
#    P6_l = 27000.0
#    P6_s = 1000.0
#
#    P6 = (P6_l*np.ones((Nt,1)) + np.random.normal(loc=0.0, scale=P6_s, size=(Nt,1)))
#
#    P_matrix = np.column_stack((P1,P2,P3,P4,P5,P6))
    
 #   return P_matrix

