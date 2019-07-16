#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:27:29 2019

@author: lejoflores
"""

import numpy as np
import matplotlib.pyplot as plt
import CropDecider as cd

Nt = 30
Nens = 100

t = np.arange(Nt)

P1_ini = 30000.0
P1_fin = 15000.0
P1_var = 1000.0

P2_ini = 20000.0
P2_fin = 23000.0
P2_var = 1000.0

a_ra = 4.5
b_ra = 1.0

a_ea = 0.5
b_ea = 3.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100




P1 = np.zeros((Nt,Nens))
P2 = np.zeros((Nt,Nens))

Switch_ra = np.zeros((Nt,Nens))
Switch_ea = np.zeros((Nt,Nens))

fig,ax = plt.subplots(nrows=2,ncols=1,figsize=(12,14))

for i in np.arange(Nens):
    
    P1[:,i] = (np.linspace(P1_ini,P1_fin,num=Nt).reshape(Nt) + np.random.normal(loc=0.0, scale=P1_var, size=(Nt)))
    P2[:,i] = (np.linspace(P2_ini,P2_fin,num=Nt).reshape(Nt) + np.random.normal(loc=0.0, scale=P2_var, size=(Nt)))
    
    ax[0].plot(t,P1[:,i],color=[0.7,0.7,0.7])
    ax[0].plot(t,P2[:,i],color=[0.4,0.4,0.4])
    
    for time in t:
        Switch_ra[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P1[time,i],P2[time,i])
        Switch_ea[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P1[time,i],P2[time,i])
    

ProbSwitch_ra = np.sum(Switch_ra,axis=1)/Nens
ProbSwitch_ea = np.sum(Switch_ea,axis=1)/Nens

ax[1].plot(t,ProbSwitch_ra,label='Switching resistant')
ax[1].plot(t,ProbSwitch_ea,label='Switching tolerant')

ax[0].set_ylabel('Profit [$]')
ax[0].set_ylim([10000,35000])
ax[1].set_ylabel('Fraction of Farmers that Switched [-]')
ax[1].set_xlabel('Time [yr]')

plt.savefig('Exp1.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')    
    