#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 15:09:10 2019

@author: kek25

Library of functions for geospatial processing

minDistCity - Calculates the distance from any cell to a city cell of any density category. It requires np.array of SRP GCAM categories, otherwise city cells will not be identified properly.
"""
import numpy as np
import matplotlib.pyplot as plt

#read in from file
#file ='/Users/kek25/Documents/GitRepos/IM3-BoiseState/ABMdev/Data/gcam_1km_2010_AdaCanyon.npy'
#gcam=np.load(file)

def minDistCity(gcam):
    
    #assert gcam.max <=28, "Array does not conform to SRP GCAM categories" had to remove, bc it was throwing error
    
    from scipy import spatial
    urban_bool= np.logical_or(np.logical_or(gcam[0] == 26, gcam[0] == 27), np.logical_or(gcam[0] == 17, gcam[0] == 25)) 
    
    rur=np.where(np.logical_and(~urban_bool, gcam[0] != 0)) 
    rural=np.array((rur[0],rur[1])).transpose()
    
    urb=np.where(urban_bool)
    urban = np.array((urb[0], urb[1])).transpose()
    
    tree = spatial.cKDTree(urban)
    mindist, minid = tree.query(rural)
    #reconstruct 2D np array with distance values
    urb_val=np.zeros(urban.shape[0])
    idx = np.vstack((urban, rural))
    dist= np.vstack((urb_val[:, None], mindist[:, None]))
    out=np.zeros(gcam[0].shape)
    out.fill(np.nan)
    for i in np.arange(dist.size):
        out[idx[i,0]][idx[i,1]]= dist[i]
    return(out)
    
    
#dist2city=minDistCity(lc)
#should we save this output every time?
#np.save('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/ABMdev/Data/dist2city_1km_2010_AdaCanyon.npy', dist2city)

#------------------------------------------------
#Save output
#------------------------------------------------

def saveLC(temp_lc, startYear, iteration, DataPath):
    
    year= str(startYear + iteration)
    
    outfile = DataPath+'ABMdev/Output/lc_'+year+'.npy'
    
    np.save(outfile, temp_lc)
    
    return
    
#------------------------------------------------
#convert agent array to np array for plotting -- 
#------------------------------------------------

def plotAgents(AgentArray, nRows, nCols):
    Agents=np.empty((nRows,nCols))   
    for i in np.arange(nRows):
        for j in np.arange(nCols):
            if (AgentArray[i][j]=='aFarmer'):
                Agents[i][j] = 4
            elif (AgentArray[i][j]=='aUrban'):
                Agents[i][j] = 2
            elif (AgentArray[i][j]=='water'):
                Agents[i][j] = 3
            elif (AgentArray[i][j]=='empty'):
                Agents[i][j] = 1
    return(plt.imshow(Agents))
    
    