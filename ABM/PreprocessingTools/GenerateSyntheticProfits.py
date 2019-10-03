#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 14:23:05 2019

@author: lejoflores
"""


import numpy as np
import sys
import csv

Num_crops = 3
# TODO: This gets added to the config file
NPRICE_FUNCTIONS = Num_crops
#=============================================================================#
#                                                                             #
#                                                                             #
#=============================================================================#
def GeneratePrice_linear(Nt,Pi,Pf,perturb,s_p=0.0):
    """Description
    
    :param Nt: Number of timesteps in the model             
    :param Pi: Profit at the beginning of the time series
    :param Pf: Profit at the end of the time series
    :param perturb: Perturbation flag. 0 = no random perturbations to profit. 1 = add zero mean, uncorrelated noise to every time step
    :param s_p: Standard deviation of noise added to profit signal at each time step (default = 0.0)
                
    :return: An Nt x 1 numpy array of profit
    """
    P = np.linspace(Pi,Pf,num=Nt).reshape((Nt,1))
    if(perturb==1):
        P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))
    
    return P

#=============================================================================#
#                                                                             #
#                                                                             #
#=============================================================================#
def GeneratePrice_step(Nt,Pi,Pf,t_step,perturb,s_p=0.0):
    """Description
    
    :param Nt: Number of timesteps in the model        
    :param Pi: Profit prior to the step change
    :param Pf: Profit after the step change
    :param t_step: (0.0 to 1.0) the time at which the step change occurs as a fraction of Nt
    :param perturb: Perturbation flag. 0 = no random perturbations to profit. 1 = add zero mean, uncorrelated noise to every time step
    :param s_p: Standard deviation of noise added to profit signal at each time step (default = 0.0)
                
    :return: An Nt x 1 numpy array of profit
    """
    assert t_step > 0.0, 'GenerateSyntheticPrices.py ERROR: Step price change time is less than 0.0'
    assert t_step < 1.0, 'GenerateSyntheticPrices.py ERROR: Step price change time is greeater than 1.0'
    
    
    P = np.zeros((Nt,1))
    P[0:(int(t_step*Nt))] = Pi
    P[(int(t_step*Nt)):]  = Pf

    if(perturb==1):
        P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))

    return P

#=============================================================================#
#                                                                             #
#                                                                             #
#=============================================================================#
def GeneratePrice_periodic(Nt,Pmag,Pamp,n_period,perturb,s_p=0.0):
    """Description
    
    :param Nt: Number of timesteps in the model             
    :param Pmag: 
    :param Pamp:                
    :param n_period:   
    :param perturb: Perturbation flag. 0 = no random perturbations to profit. 1 = add zero mean, uncorrelated noise to every time step
    :param s_p: Standard deviation of noise added to profit signal at each time step (default = 0.0)
                
    :return: An Nt x 1 numpy array of profit
    """
    x = np.linspace(0.0,n_period*2*np.pi, num=Nt).reshape((Nt,1))
    P = Pmag + Pamp  * np.sin(x)
    
    if(perturb==1):
        P += np.random.normal(loc=0.0, scale=s_p, size=(Nt,1))
      
    return P

#=============================================================================#
#                                                                             #
#                                                                             #
#=============================================================================#
def main(argv):
    """Description
    
    :param argv: Array of 5 command line arguments passed from the __main__ function   
    :param argv[0]: Name of this function (GenerateSyntheticPrices)               
    :param argv[1]: Number of crops expect to create profit time series for
    :param argv[2]: Number of timesteps in the time series
    :param argv[3]: Name of CSV file that contains information about the crops, including parameters of the generator functions, for which profits are generated and including path if CSV file is in a different directory
    :param argv[4]: Name of CSV file to which profit time series will be written, including path to output if in a different directory than the script

    :return: null (output written to file)
    """
    
    if(len(argv)!=5):
        print('\nERROR: Incorrect number of command line arguments\n')
        print('Usage: GenerateSyntheticPrices.py <no. crops> <no. timesteps> <Input CSV file> <Output CSV file>\n')
        print('\tGenerateSyntheticPrices.py = Name of this python script')
        print('\t<no. crops>                = Number of crops to synthesize prices for')
        print('\t<no. timesteps>            = Number of timesteps to generate prices for')
        print('\t<CSV file>                 = CSV file containing crop information')
        print('\t                             (see documentation)')
        print('\t<Output CSV file>          = CSV filel in which to save output prices\n')
        sys.exit()
    
    Nc          = int(argv[1])
    Nt          = int(argv[2])
    CropFileIn  = argv[3]
    CropFileOut = argv[4]
    
    # Error traps
    assert Nc > 0, 'GenerateSyntheticPrices.py ERROR: Negative number of crops encountered'
    assert Nt > 0, 'GenerateSyntheticPrices.py ERROR: Negative number of timesteps encountered'
    assert Nc <= 28, 'GenerateSyntheticPrices.py ERROR: Too many crops encountered'
    
    # Try opening the CSV file provided as input 
    try:
        fp = open(CropFileIn)
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
        
        assert int(row[2])>0, 'GenerateSyntheticPrices.py ERROR: Invalid price function behavior flag'
        assert int(row[2])<(NPRICE_FUNCTIONS+1), 'GenerateSyntheticPrices.py ERROR: Invalid price function behavior flag'
        
        price_fxn_type = int(row[2])
        
        if(price_fxn_type==1): # Linear ramp (use for linearlly increasing, decreasing, constant prices)
            assert len(row)==7,'GenerateSyntheticPrices.py ERROR: Incorrect number of parameters for linear ramp in row ' + str(CropCount)
            
            Pi       = float(row[3])
            Pf       = float(row[4])
            perturb  = int(row[5])
            if(perturb==1):
                s_p      = float(row[6])
            else:
                s_p = 0.0
            
            P = GeneratePrice_linear(Nt,Pi,Pf,perturb,s_p)
            
        elif(price_fxn_type==2): # Step function (use for step increase or decrease in price)
            assert len(row)==8,'GenerateSyntheticPrices.py ERROR: Incorrect number of parameters for step change in row ' + str(CropCount)
            
            Pi      = float(row[3])
            Pf      = float(row[4])
            t_step  = float(row[5])
            perturb = int(row[6])
            if(perturb==1):
                s_p     = float(row[7])
            else:
                s_p = 0.0
    
            P = GeneratePrice_step(Nt,Pi,Pf,t_step,perturb,s_p)
            
        elif(price_fxn_type==3): # Sinusoidal fluctuation in price
            assert len(row)==8,'GenerateSyntheticPrices.py ERROR: Incorrect number of parameters for periodic price in row ' + str(CropCount)
            
            Pmag = float(row[3])
            Pamp = float(row[4])
            n_period = float(row[5])
            perturb  = int(row[6])
            if(perturb==1):
                s_p      = float(row[7])
            else:
                s_p = 0.0
            
            P = GeneratePrice_periodic(Nt,Pmag,Pamp,n_period,perturb,s_p)   
    
        if(CropCount==1):
            P_allcrops = P
        else:
            P_allcrops = np.column_stack((P_allcrops,P))
            
    if(CropCount!=Nc):
        print('\nERROR: Mismatch in number of crops read and provided as input\n')
        print(str(Nc)+' crops were expected, '+str(CropCount)+' were read. Check input\n')
        sys.exit()
    
    
    with open(CropFileOut,'w') as fp:
        wr = csv.writer(fp, quoting=csv.QUOTE_ALL)
        wr.writerow(crop_names)
        
        wr = csv.writer(fp, quoting=csv.QUOTE_NONE)
        wr.writerow(crop_ids)
        
        np.savetxt(fp,P_allcrops,delimiter=',',fmt='%.2f')
        
        fp.close()
        
    
    
if __name__ == "__main__":
    main(sys.argv)    
