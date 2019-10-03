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
def CropPerc(CropID_all, CropIDs, Nt, Nc, scale, ResultsPath, key_file, ag_cats):
    agTot=59 #need to automate what the total area in crops is - this will be a unit test when urban isnt changing
    #np.any(CropID_all == CropIDs)
    names = []
    percentages=np.zeros((Nc, Nt))
    for c in np.arange(Nc):
        name='percentages['+str(c)+',:]'
        names.append(name)
        for t in np.arange(Nt):
            CropIx=CropIDs[c]
            percentages[c,t]=np.sum((CropID_all[t,:,:] == CropIx))/agTot*100.0
            
    t = np.arange(Nt)
    plt.rcParams.update({'font.size': 16})
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(12,12))
    
    #set colors to come color scheme w Nc colors
    #figure out how to automate the number of percentages in the stackplot
    ax.stackplot(t,percentages[0,:], percentages[1,:], percentages[2,:], percentages[3,:], labels=key_file['GCAM_SRB_Name'][ag_cats[0]]) 
    ax.set_xlim([0,Nt-1])
    ax.set_ylim([0,100])
    ax.grid()
    ax.legend(loc='lower left')
    
    ax.set_ylabel('Percent Crop Choice')  
    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')  
  
    plt.savefig(ResultsPath+'CropPercentages_'+str(scale)+'m_'+str(Nt)+'yr'.png,dpi=300,facecolor='w', edgecolor='w', 
                bbox_inches='tight')
              
def AgentAges(domain, AgentArray, Ny, Nx):
    FarmerAges=[]
    for i in np.arange(Ny):
        for j in np.arange(Nx):
            if(AgentArray[i,j]=='aFarmer'):  
                FarmerAges=np.append(FarmerAges, domain[i,j].FarmerAgents[0].Age)
                
    plt.hist(FarmerAges)