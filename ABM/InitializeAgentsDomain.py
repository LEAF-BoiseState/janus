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
import pandas as pd 

def InitializeDomain(Ny,Nx):
    "Initialize domain"
    
    dFASM = np.empty((Ny,Nx), dtype=object) #domain 

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            dFASM[i][j] = cell.dCellClass()
        #whats a unit test for this??"
    return (dFASM)

def PlaceAgents(Ny,Nx, lc, dist2city, key_file, cat_option):
    "Assign agents on the landscape"
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
    
    #still not working
    lcc=pd.DataFrame(lc[0])
    lcc.loc[lcc.isin(ag)]
    
    AgentArray[lc[0] == any(ag)] = 'aFarmer'
    
    
    AgentArray[np.logical_or(lc[0] == 28, lc[0] == 23)] ='water' 
    AgentArray[dist2city == 0] = 'aUrban'
    AgentArray[np.logical_or(lc[0] == 24, lc[0] == 21)] = 'empty' #RockIceDesert, Shrubland
  

    return (AgentArray)
#---------------------------------------
# place agent structures onto landscape and define attributes -> this is SLOW
#---------------------------------------
#Update so each of these inital values randomly selected from NASS distributions
#another way to call this re: dFASM?
def InitializeAgents(AgentArray, AgentData, dFASM, dist2city, Ny, Nx):

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            if(AgentArray[i][j]=='aFarmer'):
                 NewAgent = farmer.aFarmer(AgentData["AgeInit"], AgentData["LandStatus"], dist2city[i][j]) #this is passing actual agent data
                 dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
            if(AgentArray[i][j] =='aUrban'):
                NewAgent = urban.aUrban(AgentData["density"])
                dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
    return(dFASM)
             
