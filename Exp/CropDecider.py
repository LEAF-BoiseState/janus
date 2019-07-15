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
    