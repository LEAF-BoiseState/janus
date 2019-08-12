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
    "Initialize domain and agent array"
    AgentArray = np.empty((Ny,Nx),dtype='U10')
    dFASM = np.empty((Ny,Nx), dtype=object) #domain 

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            dFASM[i][j] = cell.dCellClass()
            
    return (AgentArray, dFASM)

def PlaceAgents(AgentArray, lc, dist2city):
    "Assign agents on the landscape"
 
    AgentArray[np.logical_and(lc[0] > 0, lc[0] <28)] = 'aFarmer'
    AgentArray[np.logical_or(lc[0] == 28, lc[0] == 23)] ='water' 
    AgentArray[dist2city == 0] = 'aUrban'
    AgentArray[np.logical_or(lc[0] == 24, lc[0] == 21)] = 'empty' #RockIceDesert, Shrubland
    AgentArray[np.logical_or(lc[0] == 19, lc[0] == 15)] = 'empty' #forest, pasture

    return (AgentArray)
#---------------------------------------
# place agent structures onto landscape and define attributes -> this is SLOW
#---------------------------------------
#Update so each of these inital values randomly selected from NASS distributions
#Initialize farmer
AgeInit = int(45.0)
nFields=1
AreaFields=np.array([10])
LandStatus=0
density=2

def InitializeAgents(AgentArray, AgentData, dFASM, dist2city, Ny, Nx):

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            if(AgentArray[i][j]=='aFarmer'):
                 NewAgent = farmer.aFarmer(AgeInit, nFields, AreaFields, LandStatus, dist2city[i][j])
                 dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
            if(AgentArray[i][j] =='aUrban'):
                NewAgent = urban.aUrban(density)
                dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
    return(dFASM)
             
