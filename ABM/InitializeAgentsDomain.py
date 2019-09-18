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
#Update so each of these inital values randomly selected from NASS distributions
def InitializeAgents(AgentArray, dFASM, dist2city, tenure, ages, switch, Ny, Nx):

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            #this is where the agent data pulls from distributions
            #Update so each of these inital values are randomly selected from NASS distributions
            k=np.random()
            #randomly select 0/1 to determing if farmer is switching averse or tolerant from "switch" param set
            AgentData = {
                    "AgeInit" : int(45.0),
                    "LandStatus" : 0,
                    "density" : 2,
                    "alpha": switch[k][1],
                    "beta": switch[k][1],
                    "nFields": 1
            }
            
            if(AgentArray[i][j]=='aFarmer'):
                 NewAgent = farmer.aFarmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"], Dist2city=dist2city[i][j], nFields=AgentData['nFields'], alpha = AgentData['alpha'], beta = AgentData['beta']) #this is passing actual agent data
                 dFASM[i][j].AddAgent(NewAgent)
            if(AgentArray[i][j] =='aUrban'):
                NewAgent = urban.aUrban(density=AgentData["density"])
                dFASM[i][j].AddAgent(NewAgent)
    return(dFASM)
             
