#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:27:29 2019

@author: lejoflores
"""

import numpy as np
import matplotlib.pyplot as plt
import CropDecider as cd

Nt = 31
Nens = 1000

t = np.arange(Nt)

P1_ini = 30000.0
P1_fin = 15000.0
P1_var = 1000.0

P2_ini = 20000.0
P2_fin = 23000.0
P2_var = 1000.0

P3_max  = 30000.0
P3_slp = 100.0
P3_var = 1000.0

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
P3 = np.zeros((Nt,Nens))

Switch_ra_12 = np.zeros((Nt,Nens))
Switch_ra_13 = np.zeros((Nt,Nens))

Switch_ra_21 = np.zeros((Nt,Nens))
Switch_ra_23 = np.zeros((Nt,Nens))

Switch_ra_31 = np.zeros((Nt,Nens))
Switch_ra_32 = np.zeros((Nt,Nens))


Switch_ea_12 = np.zeros((Nt,Nens))
Switch_ea_13 = np.zeros((Nt,Nens))

Switch_ea_21 = np.zeros((Nt,Nens))
Switch_ea_23 = np.zeros((Nt,Nens))

Switch_ea_31 = np.zeros((Nt,Nens))
Switch_ea_32 = np.zeros((Nt,Nens))

Switch_ra = np.zeros((Nt,Nens))
Switch_ea = np.zeros((Nt,Nens)) 


CropChoice_ra = np.ones((Nt,Nens))
CropChoice_ea = np.ones((Nt,Nens))

fig,ax = plt.subplots(nrows=2,ncols=1,figsize=(12,14))

for i in np.arange(Nens):
    
    P1[:,i] = (np.linspace(P1_ini,P1_fin,num=Nt).reshape(Nt) + np.random.normal(loc=0.0, scale=P1_var, size=(Nt)))
    P2[:,i] = (np.linspace(P2_ini,P2_fin,num=Nt).reshape(Nt) + np.random.normal(loc=0.0, scale=P2_var, size=(Nt)))
    P3[:,i] = (P3_max - P3_slp*(t - Nt/2.0)**2 + np.random.normal(loc=0.0, scale=P3_var, size=(Nt)))
    ax[0].plot(t,P1[:,i],color=[0.7,0.7,0.7])
    ax[0].plot(t,P2[:,i],color=[0.4,0.4,0.4])
    ax[0].plot(t,P3[:,i],color=[0.2,0.2,0.2])

    for time in t[1:]:
                
        # Switching averse agents
        if(CropChoice_ra[time-1,i]==1):
            Switch_ra_12[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P1[time,i],P2[time,i])
            Switch_ra_13[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P1[time,i],P3[time,i])
            if(Switch_ra_12[time,i]==1) and (Switch_ra_13[time,i]==1):
                CropChoice_ra[time,i] = np.random.choice([2,3],1)
                Switch_ra[time,i] = 1
            elif(Switch_ra_12[time,i]==1):
                CropChoice_ra[time,i] = 2
                Switch_ra[time,i] = 1
            elif(Switch_ra_13[time,i]==1):
                CropChoice_ra[time,i] = 3
                Switch_ra[time,i] = 1
            
        elif(CropChoice_ra[time-1,i]==2):
            Switch_ra_21[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P2[time,i],P1[time,i])
            Switch_ra_23[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P2[time,i],P3[time,i])
            if(Switch_ra_21[time,i]==1) and (Switch_ra_23[time,i]==1):
                CropChoice_ra[time,i] = np.random.choice([1,3],1)
                Switch_ra[time,i] = 1
            elif(Switch_ra_21[time,i]==1):
                CropChoice_ra[time,i] = 1
                Switch_ra[time,i] = 1
            elif(Switch_ra_23[time,i]==1):
                CropChoice_ra[time,i] = 3
                Switch_ra[time,i] = 1

        elif(CropChoice_ra[time-1,i]==3):
            Switch_ra_31[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P3[time,i],P1[time,i])
            Switch_ra_32[time,i] = cd.Decide(a_ra,b_ra,fmin,fmax,n,P3[time,i],P2[time,i])
            if(Switch_ra_31[time,i]==1) and (Switch_ra_32[time,i]==1):
                CropChoice_ra[time,i] = np.random.choice([1,2],1)
                Switch_ra[time,i] = 1
            elif(Switch_ra_31[time,i]==1):
                CropChoice_ra[time,i] = 1
                Switch_ra[time,i] = 1
            elif(Switch_ra_32[time,i]==1):
                CropChoice_ra[time,i] = 2
                Switch_ra[time,i] = 1
            
        # Switching tolerant case
        if(CropChoice_ea[time-1,i]==1):
            Switch_ea_12[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P1[time,i],P2[time,i])
            Switch_ea_13[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P1[time,i],P3[time,i])
            if(Switch_ea_12[time,i]==1) and (Switch_ea_13[time,i]==1):
                CropChoice_ea[time,i] = np.random.choice([2,3],1)
                Switch_ea[time,i] = 1
            elif(Switch_ea_12[time,i]==1):
                CropChoice_ea[time,i] = 2
                Switch_ea[time,i] = 1
            elif(Switch_ea_13[time,i]==1):
                CropChoice_ea[time,i] = 3
                Switch_ea[time,i] = 1
            
        elif(CropChoice_ea[time-1,i]==2):
            Switch_ea_21[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P2[time,i],P1[time,i])
            Switch_ea_23[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P2[time,i],P3[time,i])
            if(Switch_ea_21[time,i]==1) and (Switch_ea_23[time,i]==1):
                CropChoice_ea[time,i] = np.random.choice([1,3],1)
                Switch_ea[time,i] = 1
            elif(Switch_ea_21[time,i]==1):
                CropChoice_ea[time,i] = 1
                Switch_ea[time,i] = 1
            elif(Switch_ea_23[time,i]==1):
                CropChoice_ea[time,i] = 3
                Switch_ea[time,i] = 1

        elif(CropChoice_ea[time-1,i]==3):
            Switch_ea_31[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P3[time,i],P1[time,i])
            Switch_ea_32[time,i] = cd.Decide(a_ea,b_ea,fmin,fmax,n,P3[time,i],P2[time,i])
            if(Switch_ea_31[time,i]==1) and (Switch_ea_32[time,i]==1):
                CropChoice_ea[time,i] = np.random.choice([1,2],1)
                Switch_ea[time,i] = 1
            elif(Switch_ea_31[time,i]==1):
                CropChoice_ea[time,i] = 1
                Switch_ea[time,i] = 1
            elif(Switch_ea_32[time,i]==1):
                CropChoice_ea[time,i] = 2
                Switch_ea[time,i] = 1
            


ProbSwitch_ra = np.sum(Switch_ra,axis=1)/Nens
ProbSwitch_ea = np.sum(Switch_ea,axis=1)/Nens

ax[1].plot(t,ProbSwitch_ra,label='Switching resistant')
ax[1].plot(t,ProbSwitch_ea,label='Switching tolerant')
ax[1].legend()

ax[0].set_ylabel('Profit [$]')
ax[0].set_ylim([10000,35000])
ax[1].set_ylabel('Fraction of Farmers that Switched [-]')
ax[1].set_ylim([0,1])
ax[1].set_xlabel('Time [yr]')

plt.savefig('Exp2_plot1.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')    
    

PercentLU1_ra = np.sum((CropChoice_ra==1),axis=1)/Nens*100.0
PercentLU2_ra = np.sum((CropChoice_ra==2),axis=1)/Nens*100.0
PercentLU3_ra = np.sum((CropChoice_ra==3),axis=1)/Nens*100.0

PercentLU1_ea = np.sum((CropChoice_ea==1),axis=1)/Nens*100.0
PercentLU2_ea = np.sum((CropChoice_ea==2),axis=1)/Nens*100.0
PercentLU3_ea = np.sum((CropChoice_ea==3),axis=1)/Nens*100.0


fig,ax = plt.subplots(nrows=2,ncols=1,figsize=(12,14))
ax[0].stackplot(t,PercentLU1_ra,PercentLU2_ra,PercentLU3_ra,colors=['#bfe1f5','#d3edab','#eda566'])
ax[1].stackplot(t,PercentLU1_ea,PercentLU2_ea,PercentLU3_ea,colors=['#bfe1f5','#d3edab','#eda566'])

ax[0].set_xlim([0,30])
ax[0].set_ylim([0,100])
ax[0].grid()
ax[1].set_xlim([0,30])
ax[1].set_ylim([0,100])
ax[1].grid()

ax[0].set_title('Crop Choice: Switching Averse')
ax[1].set_title('Crop Choice: Switching Tolerant')
ax[0].set_ylabel('Percent Crop Choice')  
ax[1].set_ylabel('Percent Crop Choice')
ax[1].set_xlabel('Time [yr]')  
  
plt.savefig('Exp2_plot2.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')    
    