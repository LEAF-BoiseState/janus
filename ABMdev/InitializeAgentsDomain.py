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

def PlaceAgents(Ny,Nx, lc, dist2city):
    "Assign agents on the landscape"
    AgentArray = np.empty((Ny,Nx),dtype='U10')
    
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

def InitializeAgents(AgentArray, AgentData, dFASM, dist2city, Ny, Nx):

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            if(AgentArray[i][j]=='aFarmer'):
                 NewAgent = farmer.aFarmer(AgentData["AgeInit"], AgentData["nFields"], AgentData["AreaFields"], AgentData["LandStatus"], dist2city[i][j])
                 dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
            if(AgentArray[i][j] =='aUrban'):
                NewAgent = urban.aUrban(AgentData["density"])
                dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
    return(dFASM)
             
