#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 13:40:08 2018

@author: lejoflores
"""

import numpy as np
from scipy import special
import matplotlib.pyplot as plt


#x = np.linspace(-20.0,20.0,num=100)
# =============================================================================
# 
# alpha1 = 1.0
# alpha2 = 0.2
# alpha3 = 1.8
# 
# =============================================================================
alpha_F1 = 1.0
# =============================================================================
# 
# y1 = special.expit(alpha1*x)
# y2 = special.expit(alpha2*x)
# y3 = special.expit(alpha3*x)
# 
# plt.figure(figsize=(10,8))
# plt.plot(x,y1,label=r'$\alpha =$ '+str(alpha1))
# plt.plot(x,y2,label=r'$\alpha =$ '+str(alpha2))
# plt.plot(x,y3,label=r'$\alpha =$ '+str(alpha3))
# plt.legend()
# plt.show()
# =============================================================================


Nt = 20

AgeInit = 45.0
DistFromCityInit = 20.0
OnFIInit = 45000.0
OffFIInit = 20000.0
CropIDInit = 1

OnFI_agr = 0.03
OffFI_agr = 0.05

FarmerAge = np.zeros((Nt,2))
FarmerDistToCity = np.zeros((Nt,2))
FarmerOnFarmInc = np.zeros((Nt,2))
FarmerOffFarmInc = np.zeros((Nt,2))

IncomeDiff12 = np.zeros((Nt,1))
IncomeDiff21 = np.zeros((Nt,1))

class Farmer:
    def __init__(self, Age, DistFromCity, OnFarmIncome, OffFarmIncome, CropID):
        self.Age = Age
        self.DistFromCity = DistFromCity
        self.OnFarmIncome = OnFarmIncome
        self.OffFarmIncome = OffFarmIncome
        self.CropID = CropID

    def UpdateAge(self):
        self.Age += 1
        
    def UpdateDistFromCity(self,dx):
        self.DistFromCity += dx
    
    def UpdateOnFarmIncome(self,loc=0.0,scale=1.0):
        self.OnFarmIncome *= scale
        self.OnFarmIncome += loc

    def UpdateOffFarmIncome(self,loc=0.0,scale=1.0):
        self.OffFarmIncome *= scale
        self.OffFarmIncome += loc
        
        
myF1 = Farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 1)
myF2 = Farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 2)

for t in np.arange(Nt,dtype=int):
    

    DeltaDistToCity = ((-0.1 - -0.2)*np.random.random() - 0.2)    
    OnFI_gr = 1.0 + OnFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)    
    OffFI_gr = 1.0 + OffFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)

    myF1.UpdateAge()
    myF1.UpdateDistFromCity(DeltaDistToCity)
    myF1.UpdateOnFarmIncome(scale=OnFI_gr)
    myF1.UpdateOffFarmIncome(scale=OffFI_gr)

    DeltaDistToCity = ((-0.1 - -0.2)*np.random.random() - 0.2)    
    OnFI_gr = 1.0 + OnFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)    
    OffFI_gr = 1.0 + OffFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)
    
    myF2.UpdateAge()
    myF2.UpdateDistFromCity(DeltaDistToCity)
    if(t==10):
        myF2.UpdateOnFarmIncome(loc=20000)        
    else:
        myF2.UpdateOnFarmIncome(scale=OnFI_gr)
    myF2.UpdateOffFarmIncome(scale=OffFI_gr)
    
    
    # Compute the difference in on-farm income between Farmers 1 and 2
    IncomeDiff12[t] = myF1.OnFarmIncome - myF2.OnFarmIncome
    IncomeDiff21[t] = myF2.OnFarmIncome - myF1.OnFarmIncome
    
    # Determine where this falls on the logit 
    x = alpha_F1*(IncomeDiff12[t] - 20000)/myF1.OnFarmIncome
    p = special.expit(x)
    print('Value of logit function = '+str(p))
    
    FarmerAge[t][0] = myF1.Age
    FarmerDistToCity[t][0] = myF1.DistFromCity
    FarmerOnFarmInc[t][0] = myF1.OnFarmIncome
    FarmerOffFarmInc[t][0] = myF1.OffFarmIncome

    FarmerAge[t][1] = myF2.Age
    FarmerDistToCity[t][1] = myF2.DistFromCity
    FarmerOnFarmInc[t][1] = myF2.OnFarmIncome
    FarmerOffFarmInc[t][1] = myF2.OffFarmIncome

    
plt.figure(figsize=(10,12))
plt.subplot(3,1,1)
plt.plot(np.arange(Nt),FarmerOnFarmInc[:,1],label='On Farm Income')
plt.plot(np.arange(Nt),FarmerOffFarmInc[:,1],label='Off Farm Income')
plt.plot(np.arange(Nt),FarmerOnFarmInc[:,1]+FarmerOffFarmInc[:,1],label='Total Income')
plt.ylim([0,120000])
plt.title('Farmer 1 Income [$]')
plt.legend()

plt.subplot(3,1,2)
plt.plot(np.arange(Nt),FarmerOnFarmInc[:,1],label='On Farm Income')
plt.plot(np.arange(Nt),FarmerOffFarmInc[:,1],label='Off Farm Income')
plt.plot(np.arange(Nt),FarmerOnFarmInc[:,1]+FarmerOffFarmInc[:,1],label='Total Income')
plt.ylim([0,120000])
plt.title('Farmer 2 Income [$]')
plt.legend()


plt.subplot(3,1,3)
plt.plot(np.arange(Nt),IncomeDiff12,label='Farmer 1 - Farmer 2 income')
plt.plot(np.arange(Nt),IncomeDiff21,label='Farmer 2 - Farmer 1 income')
plt.title('Income differences between farmers [$]')
plt.legend()


