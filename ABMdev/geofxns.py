#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 15:09:10 2019

@author: kek25

Library of functions for geospatial processing

minDistCity - Calculates the distance from any cell to a city cell of any density category. It requires np.array of SRP GCAM categories, otherwise city cells will not be identified properly.
"""
import numpy as np

#read in from file
#file ='/Users/kek25/Documents/GitRepos/IM3-BoiseState/ABMdev/Data/gcam_1km_2010_AdaCanyon.npy'
#gcam=np.load(file)

def minDistCity(gcam):
    
    #assert gcam.max <=28, "Array does not conform to SRP GCAM categories"
    
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

#np.save('/Users/kendrakaiser/Documents/GitRepos/IM3-BoiseState/ABMdev/Data/dist2city_1km_2010_AdaCanyon.npy', dist2city)