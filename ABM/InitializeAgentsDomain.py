#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 11:15:12 2019

@author: kek25
"""
import numpy as np
import Classes.aFarmer as farmer
import Classes.dCellClass as cell
import Classes.aUrban as urban

def InitializeDomain(Ny,Nx):
    "Initialize domain"
    
    dFASM = np.empty((Ny,Nx), dtype=object) #domain 

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            dFASM[i][j] = cell.dCellClass()
        #whats a unit test for this??"
    return (dFASM)

def PlaceAgents(Ny,Nx, lc, key_file, cat_option):
    #assert that cat_option has to be a header in the csv doc
    AgentArray = np.empty((Ny,Nx),dtype='U10')
    
    if cat_option =='SRB':
        agent_Cat=key_file['SRB_cat'][0:28]
        code=key_file['SRB_GCAM_id_list'][0:28]
    elif cat_option =='GCAM':
        agent_Cat=key_file['GCAM_cat'][0:24]
        code=key_file['GCAM_id_list'][0:24]
    
    ag=np.array(code[agent_Cat == 'ag']).astype(int)
    urb=np.array(code[agent_Cat == 'urb']).astype(int)
    water=np.array(code[agent_Cat == 'water']).astype(int)
    empty=np.array(code[agent_Cat == 'nat']).astype(int)
    
    #this works, would be better without the for loops
    for i in ag:
        AgentArray[lc[0] == i] = 'aFarmer'
    for i in water:
        AgentArray[lc[0] == i] = 'water'
    for i in urb:
        AgentArray[lc[0] == i] = 'aUrban'
    for i in empty:
        AgentArray[lc[0] == i] = 'empty'
  
    return (AgentArray)
#---------------------------------------
# place agent structures onto landscape and define attributes -> this is Not working
#---------------------------------------
def InitializeAgents(AgentArray, dFASM, dist2city, TenureCDF, AgeCDF, switch, Ny, Nx, lc, p):
     #agent data pulled from distributions
   
    for i in np.arange(Ny):
        for j in np.arange(Nx):
           
            ss=np.random.random_sample()
            ts = np.random.random_sample() 
            ageS = np.random.random_sample()
            print(ageS)
            
            if ss >= p:
                k= 0
            else: k =1
            
            if ageS < AgeCDF[0][1]:
                ageI = 18
            else: 
                ageT=np.where(AgeCDF[:,[1]] <= ageS)
                ageI=max(ageT[0])
            
            tt=np.where(TenureCDF[:,[1]] >= ts)
            tenStat=min(tt[0])
            
            if(AgentArray[i][j]=='aFarmer'):
                 AgentData = {
                    "AgeInit" : ageI,
                    "LandStatus" : tenStat,
                    "Alpha": switch[k][1],
                    "Beta": switch[k][1],
                    "nFields": 1
                }
                
                 NewAgent = farmer.aFarmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"], Dist2city=dist2city[i][j], nFields=AgentData['nFields'], alpha = AgentData['Alpha'], beta = AgentData['Beta']) #this is passing actual agent data
                 dFASM[i][j].AddAgent(NewAgent)
                 
            if(AgentArray[i][j] =='aUrban'):
                lcD = lc[0][i][j] #pull the landcover category from the landcover, set this so it's 0 =open space, 1=low, 2=med, 3=high density
                if lcD == 17:
                    d=3
                elif lcD == 25:
                    d=2
                elif lcD == 26:
                    d=1
                elif lcD == 27:
                    d=0
                
                AgentData = {
                    "Density" : d,
                }
                NewAgent = urban.aUrban(density=AgentData["Density"])
                dFASM[i][j].AddAgent(NewAgent)
    
    return(dFASM)
             
