#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 15:35:49 2019

@author: kek25
"""
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def CreateAnimation(CropID_all, Nt):
    ims = []

    fig = plt.figure(figsize=(12,12))
    for t in np.arange(Nt):
        im = plt.imshow(CropID_all[t,:,:], interpolation='none')
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)

    ani.save('CropID_vs_Time.gif')

#line plot showing the change in landcover over time    
def dCdT(CropID_all, Nt):
    unique_elementsToat, counts_elementsToat = np.unique(CropID_all, return_counts=True)
    counts = np.zeros((len(unique_elementsToat), Nt))
    for t in np.arange(Nt):
        unique_elements, counts_elements = np.unique(CropID_all[t], return_counts=True)
        #this isn't working .. need to come up with a better way to do this
      #  loc=np.where(unique_elementsToat == unique_elements)
        counts[:, t] = counts_elements
        
    #fig = plt.figure(figsize=(12,12))
    #for c in np.arange(len(CtopIDs)):
        
        #plt.plot(np.arange(Nt)), count)
   # plt.show()
   
   
#stackplot of crops over time
#automate stackplot naming conventions
def CropPerc(crop_id_all, CropIDs, nt, nc, scale, results_path, key_file, ag_cats):
    ag_area=np.empty(shape=(nc, nt))
    for t in np.arange(nt):
       cur_crop = crop_id_all[t,:,:]
       for c in np.arange(nc):
           bools=(cur_crop == CropIDs[c])
           ag_area[c,t]=np.sum(bools)
        
    agTot = np.sum(ag_area, axis=0)

    names = []
    percentages = np.zeros((nc, nt))
    data = []
    for c in np.arange(nc):
        name = 'percentages[' + str(c) + ',:]'
        names.append(name)
        for t in np.arange(nt):
            CropIx = CropIDs[c]
            percentages[c, t] = np.sum((crop_id_all[t, :, :] == CropIx)) / agTot[t] * 100.0
        data.append(percentages[c, :])
    
    y = np.vstack(data)
    
    t = np.arange(nt)
    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12))
    
    active_crops=np.any(percentages, axis=1)
    ag3=np.transpose(np.array(ag_cats))
    ac=np.array(ag3[active_crops]).flatten()
    labs=key_file['GCAM_SRB_Name'][ac]
    
    
    ax.stackplot(t,y, labels=labs) 
    ax.set_xlim([0, nt - 1])
    ax.set_ylim([0, 100])
    ax.grid()
    ax.legend(loc='lower right')

    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, 'CropPercentages_{}m_{}yr.png'.format(scale, nt))

    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close(fig=None)

              
def AgentAges(domain, AgentArray, Ny, Nx, nt, nc, scale, results_path):
    FarmerAges=[]
    for i in np.arange(Ny):
        for j in np.arange(Nx):
            if(AgentArray[i,j]=='aFarmer'):  
                FarmerAges=np.append(FarmerAges, domain[i,j].FarmerAgents[0].Age)
                
    plt.rcParams.update({'font.size': 16})
    plt.hist(FarmerAges)
    
    output_figure = os.path.join(results_path, 'AgentAges_{}m_{}yr.png'.format(scale, nt))
    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')