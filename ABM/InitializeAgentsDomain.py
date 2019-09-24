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

def getFarmerData(TenureCDF, AgeCDF, switch, p, d2c):
    #agent data pulled from distributions
    ss=np.random.random_sample()
    ts = np.random.random_sample() 
    ageS = np.random.random_sample()
    #print(ageS)
            
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
    
    AgentData = {
            "AgeInit" : ageI,
            "LandStatus" : tenStat,
            "Alpha": switch[k][0],
            "Beta": switch[k][1],
            "nFields": 1,
            "Dist2city": d2c
                }
    return(AgentData)

def getUrbanData(lc):
      #pull the landcover category from the landcover, set this so it's 0 =open space, 1=low, 2=med, 3=high density
      #this needs to be set by user based on what their landcover classes are, e.g. denisty would not be a category with original GCAM cats
      if lc == 17:
          d=3
      elif lc == 25:
          d=2
      elif lc == 26:
          d=1
      elif lc == 27:
          d=0
      AgentData = {"Density" : d}
      
      return(AgentData)
#---------------------------------------
# place agent structures onto landscape and define attributes -> this is Not working
#---------------------------------------
def InitializeAgents(AgentArray, dFASM, dist2city, TenureCDF, AgeCDF, switch, Ny, Nx, lc, p):
     
   
    for i in np.arange(Ny):
        for j in np.arange(Nx):
           
            if(AgentArray[i][j]=='aFarmer'):
                 
                 AgentData=getFarmerData(TenureCDF, AgeCDF, switch, p, dist2city[i][j])
                 NewAgent = farmer.aFarmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"], Dist2city=AgentData["Dist2city"], nFields=AgentData['nFields'], alpha = AgentData['Alpha'], beta = AgentData['Beta']) #this is passing actual agent data
                 dFASM[i][j].AddAgent(NewAgent)
                 
            if(AgentArray[i][j] =='aUrban'):
                AgentData =getUrbanData(lc[0][i][j])
                NewAgent = urban.aUrban(density=AgentData["Density"])
                dFASM[i][j].AddAgent(NewAgent)
    
    return(dFASM)
             
