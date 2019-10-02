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
import PreprocessingTools.getNASSAgentData as getNASS

def InitializeDomain(Ny,Nx):
    
    domain = np.empty((Ny,Nx), dtype=object) 

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            domain[i][j] = cell.dCellClass()
        #whats a unit test for this??"
    return (domain)

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

#------------------------------------------------------------------------------
# place agent structures onto landscape and define attributes 
#------------------------------------------------------------------------------
def Agents(AgentArray, domain, dist2city, TenureCDF, AgeCDF, switch, Ny, Nx, lc, p):
     
   
    for i in np.arange(Ny):
        for j in np.arange(Nx):
           
            if(AgentArray[i][j]=='aFarmer'):
                 
                 AgentData=getNASS.FarmerData(TenureCDF, AgeCDF, switch, p, dist2city[i][j])
                 NewAgent = farmer.aFarmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"], Dist2city=AgentData["Dist2city"], nFields=AgentData['nFields'], alpha = AgentData['Alpha'], beta = AgentData['Beta']) #this is passing actual agent data
                 domain[i][j].AddAgent(NewAgent)
                 
            if(AgentArray[i][j] =='aUrban'):
                AgentData =getNASS.UrbanData(lc[0][i][j])
                NewAgent = urban.aUrban(density=AgentData["Density"])
                domain[i][j].AddAgent(NewAgent)
    
    return(domain)
             
#
#
#
    
def Profits(profit_file, Nt, Ny, Nx, CropID_all, CropIDs):
    """Decide which crop and associated profit to pick out of two options.
    
    :param profit_file: data frame of profit signals creatd from generate synthetic prices, or user supplied         
    :param Nt:                
    :param Ny:                
    :param Nx:
    :param CropID_all: Nt x Nx x Ny np array of current landcover              
    :param CropIDs: Num_crop x 1 np array of crop ids             
                
    :return: np array of initial profits based on price signals                       
    """
    
    profits_actual = np.zeros((Nt,Ny,Nx))
    profit_signals=profit_file.to_numpy()
    for i in np.arange(Ny):
        for j in np.arange(Nx):
            CropInd= CropID_all[0,i,j]
            CropIx=np.where(CropIDs == CropInd)
            if CropInd in (CropIDs):
                profits_actual[0,i,j]= profit_signals[CropIx[0][0],0]
            else:
                profits_actual[0,i,j]= 0
                    
    return(profits_actual)