#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 12:12:43 2019

@author: lejoflores
"""
import numpy as np
import scipy.special as sp

# Not sure if this is needed if we can get scipy to return the value of the 
# CDF
def SwitchingProbCurve(alpha,beta,fmin,fmax,n,profit):
    
    x  = np.linspace(0,1.0,num=n)
    
    fx = sp.betainc(alpha,beta,x)
    
    x2 = np.linspace(fmin*profit,fmax*profit,num=n)
    
    return x2, fx


#=============================================================================#
#                                                                             #
# Decide: Choose from among two different alternatives 
#                                                                             #
#=============================================================================#
def Decide(alpha,beta,fmin,fmax,n,profit,profit_p):

    if(profit_p>profit):
        
        x,fx = SwitchingProbCurve(alpha,beta,fmin,fmax,n,profit)
        
        prob_switch = np.interp(profit_p,x,fx)
        
        if(np.random.rand(1) < prob_switch):
            return 1 # Switch
        else:
            return 0 # Do not switch
        
    else:
        return 0 # Do not switch if not profitable


#=============================================================================#
#                                                                             #
# DecideN: Choose from among N different crops, all with associated anti-     #
#          cipated proft values.                                              #
#                                                                             #
#=============================================================================#
def DecideN(alpha, beta, fmin, fmax, n, profit, vec_crops, 
            vec_profit_p, rule=True):

    # Key assumptions: the vector of crop IDs and anticipated profits associated
    # with each crop must both be N x 1 column vectors. Error trap this below:
    assert (vec_crops.shape == vec_profit_p.shape), \
        'Supplied vector of crop IDs and potential profits must be identical'
    assert (vec_crops.shape[1] == 1), \
        'Supplied vector of crop IDs and potential profits must be N x 1'
    
    # Create a boolean vector to store a 0 or 1 if the farmer will select the
    # crop (==1) or not (==1)
    AccRej =  np.zeros(vec_crops.shape,dtype='int') 
    
    for i in np.arange(AccRej.size):
        # Use the `Decide` function above to choose whether or not the crop is
        # viable
        AccRej[i] = Decide(alpha,beta,fmin,fmax,n,profit,vec_profit_p[i])

    # Find the Crop IDs and associated profits that were returned as "viable" 
    # based on the "Decide" function (that is, Decide came back as "yes" == 1)
    ViableCrops   = vec_crops[AccRej==1]
    ViableProfits = vec_profit_p[AccRej==1]

    if(ViableCrops.size==0):
        return -1, -1
    
    # Find the maximum anticipated profit and the crop IDs associated with that 
    # maximum
    MaxProfit     = ViableProfits.max()  
    MaxProfitCrop = ViableCrops[ViableProfits==MaxProfit]
    
    # This next part should be rare. There happen to be more than one viable  
    # crops that carry the same anticipated profit that also coincides with 
    # the maximum anticipated profit. The choice here is to choose randomly
    # from among those crops that have the same (maximum) profit
    if(MaxProfitCrop.size>1):        
        ViableCrops   = MaxProfitCrop
        ViableProfits = ViableProfits[ViableProfits==MaxProfit]
        rule = False # Switch rule to trick the algorithm into using the random option
    
    if(rule): # Return crop with largest profit
        CropChoice = MaxProfitCrop
        ProfitChoice = MaxProfit
        
    else: # Choose randomly from among all viable crops
        indChoice    = np.random.choice(np.arange(ViableCrops.size),size=1)
        CropChoice   = ViableCrops[indChoice]
        ProfitChoice = ViableProfits[indChoice]
        
    # Return the crop choice and associated profit
    return CropChoice, ProfitChoice

#=============================================================================#
#                                                                             #
# GeneratePrices: Generates 6 synthetic crop profits with different           #
#                 behaviors. This function is largely for debugging purposes  #
#                 to test new model test cases, etc.                          #
#                                                                             #
#=============================================================================#

def GeneratePrices(Nt):
    
    # Crop 1 = Steadily increasing
    P1_i = 20000.0
    P1_f = 31000.0
    P1_s = 1000.0

    P1 = (np.linspace(P1_i,P1_f,num=Nt).reshape((Nt,1)) + np.random.normal(loc=0.0, scale=P1_s, size=(Nt,1)))
    
    # Crop 2
    P2_i = 30000.0
    P2_f = 15000.0
    P2_s = 1000.0
    
    P2 = (np.linspace(P2_i,P2_f,num=Nt).reshape((Nt,1)) + np.random.normal(loc=0.0, scale=P2_s, size=(Nt,1)))
    
    # Crop 3 = Sinusoidal fluctuation
    P3_l = 28000.0
    P3_a = 5000.0
    P3_n = 2.0
    P3_s = 1000.0
    
    x3 = np.linspace(0.0, P3_n*2*np.pi, num=Nt).reshape((Nt,1))
    P3 = (P3_l + P3_a*np.sin(x3) + np.random.normal(loc=0.0, scale=P3_s, size=(Nt,1)))
    
    # Crop 4 = Step decrease
    P4_i = 31000.0
    P4_f = 14000.0
    P4_s = 1000.0
    
    P4 = np.zeros((Nt,1))
    P4[0:(int(P4.size/2))] = P4_i
    P4[(int(P4.size/2)):]  = P4_f
    P4 += np.random.normal(loc=0.0, scale=P4_s, size=(Nt,1))
    
    # Crop 5 = Step increase
    P5_i = 10000.0
    P5_f = 30000.0
    P5_s = 1000.0

    P5 = np.zeros((Nt,1))
    P5[0:(int(P5.size/2))] = P5_i
    P5[(int(P5.size/2)):]  = P5_f
    P5 += np.random.normal(loc=0.0, scale=P5_s, size=(Nt,1))
    
    # Crop 6 = Constant with noise
    P6_l = 27000.0
    P6_s = 1000.0

    P6 = (P6_l*np.ones((Nt,1)) + np.random.normal(loc=0.0, scale=P6_s, size=(Nt,1)))

    P_matrix = np.column_stack((P1,P2,P3,P4,P5,P6))
    
    return P_matrix

#=============================================================================#
#                                                                             #
# MakeDecision: Attempt at putting all of choice parts into one function
#               VERY SLOW - this could be parallalized
#                                                                             #
#=============================================================================#

def MakeDecision(Nt, Ny, Nx, Nc, CropID_all, Profits, Profit_ant, Profit_act, a_ra, b_ra, fmin, fmax, n, CropIDs):
    for i in np.arange(1,Nt):
        for j in np.arange(Ny):
            for k in np.arange(Nx):
                # Existing Crop ID
                CurCropChoice = CropID_all[i-1,j,k]
                CurCropChoice_ind = CurCropChoice.astype('int') - 1
                #assess current and future profit of that given crop
                if (CurCropChoice_ind < 6): #change this to be a vector of possible cropIDs
                    Profit_ant_temp = Profits[i-1, CurCropChoice_ind]#last years profit
                    Profit_p   = Profits[i,:] #this years  expected profit
                    Profit_p = Profit_p.reshape(Nc,1)
                else: 
                    Profit_ant_temp = 0
                    Profit_p = np.zeros((Nc,1))
            
                #Crop Decider
                CropChoice, ProfitChoice = DecideN(a_ra, b_ra, fmin, fmax, n, Profit_ant_temp, CropIDs, \
                                                      Profit_p, rule=True)
            
                # Check if return  values indicate the farmer shouldn't switch
                #seems like this could either be part of the above function or a new one?
                if(CropChoice==-1) and (ProfitChoice==-1):
                    CropID_all[i,j,k] = CropID_all[i-1,j,k]
                    Profit_ant[i,j,k] = Profit_ant_temp
                    Profit_act[i,j,k] = Profit_ant[i,j,k] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1,1)) #this years actual profit
                else: #switch to the new crop
                    CropID_all[i,j,k] = CropChoice
                    Profit_ant[i,j,k] = ProfitChoice
                    Profit_act[i,j,k] = Profit_ant[i,j,k] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1,1))
                    
    return(CropID_all, Profit_ant, Profit_act)