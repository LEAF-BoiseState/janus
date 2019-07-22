#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 15:04:27 2019

@author: lejoflores
"""

import numpy as np
import matplotlib.pyplot as plt
import CropDecider as cd

Nc = 6
Nt = 30
Ne = 1000

a_ra = 4.5
b_ra = 1.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100

## Choose from among 6 crops
# Crop 1 = Steadily increasing
# Crop 2 = Steadily decreasing
# Crop 3 = Sinusoidal fluctuation
# Crop 4 = Step decrease
# Crop 5 = Step increase
# Crop 6 = Constant with noise

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

# Initialize Crop IDs
CropIDs = np.arange(Nc).reshape((Nc,1)) + 1

# Initialize Crops and profits
CropID_all = np.zeros((Nt,Ne))
Profit_ant = np.zeros((Nt,Ne))
Profit_act = np.zeros((Nt,Ne))

CropID_all[0,:] = CropIDs[1]
Profit_ant[0,:] = 30000.0 + np.random.normal(loc=0.0,scale=1000.0,size=(1,Ne))
Profit_act[0,:] = Profit_ant[0,:]

# Initialize by creating price signals for all agents and all times 
P = [] # A list of numpy arrays that will be Nt x 6 crops
for i in np.arange(Ne):
    P.append(GeneratePrices(Nt))

for i in np.arange(1,Nt):
    
    for j in np.arange(Ne):
        
        Profit_ant_ij = Profit_ant[i-1,j]
        Profit_p      = P[j][i,:].reshape((Nc,1))

        # Existing Crop ID
        CurCropChoice = CropID_all[i-1,j]
        CurCropChoice_ind = CurCropChoice.astype('int') - 1
        
        CropChoice, ProfitChoice = cd.DecideN(a_ra, b_ra, fmin, fmax, n, Profit_ant_ij, CropIDs, \
            Profit_p, rule=True)

        # Check if return  values indicate the farmer shouldn't switch
        if(CropChoice==-1) and (ProfitChoice==-1):
            CropID_all[i,j] = CropID_all[i-1,j]
            Profit_ant[i,j] = P[j][i,CurCropChoice_ind]
            Profit_act[i,j] = Profit_ant[i,j] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1))
        else:
            CropID_all[i,j] = CropChoice
            Profit_ant[i,j] = ProfitChoice
            Profit_act[i,j] = Profit_ant[i,j] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1))
        

## Do a stackplot of crop choice
Percent_Crop1 = np.sum((CropID_all==1),axis=1)/Ne*100.0
Percent_Crop2 = np.sum((CropID_all==2),axis=1)/Ne*100.0
Percent_Crop3 = np.sum((CropID_all==3),axis=1)/Ne*100.0
Percent_Crop4 = np.sum((CropID_all==4),axis=1)/Ne*100.0
Percent_Crop5 = np.sum((CropID_all==5),axis=1)/Ne*100.0
Percent_Crop6 = np.sum((CropID_all==6),axis=1)/Ne*100.0

t = np.arange(Nt)

plt.rcParams.update({'font.size': 16})

fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(12,12))
ax.stackplot(t,Percent_Crop1,Percent_Crop2,Percent_Crop3,Percent_Crop4,
             Percent_Crop5,Percent_Crop6, colors=['#bfe1f5','#d3edab','#eda566',
             '#4AFFCE','#3A8A00','#005C94'], labels=['Crop 1','Crop 2','Crop 3',
             'Crop 4','Crop 5','Crop 6'])

ax.set_xlim([0,Nt-1])
ax.set_ylim([0,100])
ax.grid()
ax.legend(loc='lower left')

ax.set_ylabel('Percent Crop Choice')  
ax.set_ylabel('Percent Crop Choice')
ax.set_xlabel('Time [yr]')  
  
plt.savefig('Exp3_plot1.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')    


fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(12,12))

for i in np.arange(Ne):
    if(i==0):
        ax.plot(t,P[i][:,0],color=[0.9,0.9,0.9],label='Crop 1')
        ax.plot(t,P[i][:,1],color=[0.7,0.7,0.7],label='Crop 2')
        ax.plot(t,P[i][:,2],color=[0.5,0.5,0.5],label='Crop 3')
        ax.plot(t,P[i][:,3],color=[0.3,0.3,0.3],label='Crop 4')
        ax.plot(t,P[i][:,4],color=[0.2,0.2,0.2],label='Crop 5')
        ax.plot(t,P[i][:,5],color=[0.1,0.1,0.1],label='Crop 6')
    else:
        ax.plot(t,P[i][:,0],color=[0.9,0.9,0.9])
        ax.plot(t,P[i][:,1],color=[0.7,0.7,0.7])
        ax.plot(t,P[i][:,2],color=[0.5,0.5,0.5])
        ax.plot(t,P[i][:,3],color=[0.3,0.3,0.3])
        ax.plot(t,P[i][:,4],color=[0.2,0.2,0.2])
        ax.plot(t,P[i][:,5],color=[0.1,0.1,0.1])
    
ax.legend()
ax.grid()

ax.set_ylabel('Profit [$]')
ax.set_xlabel('Time [yr]')
ax.set_ylim([0,40000])
ax.set_xlim([0,Nt-1])

plt.savefig('Exp3_plot2.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')    
