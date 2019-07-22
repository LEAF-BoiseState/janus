#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 08:59:43 2019

@author: lejoflores
"""
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import CropDecider as cd


Nc = 6
Nt = 50
Nx = 100
Ny = 100

a_ra = 4.5
b_ra = 1.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100


# Initialize Crop IDs
CropIDs = np.arange(Nc).reshape((Nc,1)) + 1

# Initialize Crops and profits
CropID_all = np.zeros((Nt,Nx,Ny))
Profit_ant = np.zeros((Nt,Nx,Ny))
Profit_act = np.zeros((Nt,Nx,Ny))

CropID_all[0,:,:] = CropIDs[1]
Profit_ant[0,:,:] = 30000.0 + np.random.normal(loc=0.0,scale=1000.0,size=(1,Nx,Ny))
Profit_act[0,:,:] = Profit_ant[0,:,:]

# Initialize by creating price signals for all agents and all times 
P = [] # A list of numpy arrays that will be Nt x 6 crops
for i in np.arange(Nx):
    for j in np.arange(Ny):
        P.append(cd.GeneratePrices(Nt))

for i in np.arange(1,Nt):
    for j in np.arange(Nx):
        for k in np.arange(Ny):
            
            cell_coord = j*Ny + k
            
            Profit_ant_ij = Profit_ant[i-1,j,k]
            Profit_p      = P[cell_coord][i,:].reshape((Nc,1))
    
            # Existing Crop ID
            CurCropChoice = CropID_all[i-1,j,k]
            CurCropChoice_ind = CurCropChoice.astype('int') - 1
            
            CropChoice, ProfitChoice = cd.DecideN(a_ra, b_ra, fmin, fmax, n, Profit_ant_ij, CropIDs, \
                Profit_p, rule=True)
    
            # Check if return  values indicate the farmer shouldn't switch
            if(CropChoice==-1) and (ProfitChoice==-1):
                CropID_all[i,j,k] = CropID_all[i-1,j,k]
                Profit_ant[i,j,k] = P[j][i,CurCropChoice_ind]
                Profit_act[i,j,k] = Profit_ant[i,j,k] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1,1))
            else:
                CropID_all[i,j,k] = CropChoice
                Profit_ant[i,j,k] = ProfitChoice
                Profit_act[i,j,k] = Profit_ant[i,j,k] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1,1))


ims = []

fig = plt.figure(figsize=(12,12))
for t in np.arange(Nt):
    im = plt.imshow(CropID_all[t,:,:], interpolation='none')
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)

ani.save('CropID_vs_Time.gif')

plt.show()