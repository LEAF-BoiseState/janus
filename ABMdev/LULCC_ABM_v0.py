"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""
#---------------------------------------
#  Load Packages
#---------------------------------------
import geopandas as gp
import numpy as np
from geofxns import minDistCity #slow
from geofxns import saveLC #do we need to import each function, or can we just load all of them?
import Classes.aFarmer as farmer
import Classes.dCellClass as cell
import Classes.aUrban as urban
import CropFuncs.CropDecider as cd
import InitializeAgentsDomain as init

userPath='/Users/kek25/Documents/GitRepos/'
DataPath= userPath+'IM3-BoiseState/'

#---------------------------------------
# 0. Declare Variables
#---------------------------------------
#set agent switching parameters
a_ra = 4.5
b_ra = 1.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100

#---------------------------------------
# 1. Preprocessing
#---------------------------------------
#load extent
extent=gp.read_file(DataPath + 'ABMdev/Data/extent_1km_AdaCanyon.shp')
#load inital landcover
lc=np.load(DataPath + 'ABMdev/Data/gcam_1km_2010_AdaCanyon.npy')
#initalize minimum distance to city
dist2city=minDistCity(lc)

Ny, Nx = lc[0].shape
Nt = 10
#---------------------------------------
#  Initialize Crops
#---------------------------------------
Nc = 6 #there are actually 17, need random profit profiles for each of these 
CropIDs = np.arange(Nc).reshape((Nc,1)) + 1
CropID_all = np.zeros((Nt,Ny,Nx))
CropID_all[0,:,:] = lc

#---------------------------------------
#  Initialize Profits
#---------------------------------------
Profit_ant = np.zeros((Nt,Ny,Nx))
Profit_act = np.zeros((Nt,Ny,Nx))

Profit_ant[0,:,:] = 30000.0 + np.random.normal(loc=0.0,scale=1000.0,size=(1,Ny,Nx))
Profit_act[0,:,:] = Profit_ant[0,:,:]

P = [] # A list of numpy arrays that will be Nt x Nc
for i in np.arange(Ny):
    for j in np.arange(Nx):
        P.append(cd.GeneratePrices(Nt)) #slow

#---------------------------------------
#  Initialize Agents
#---------------------------------------
#Update so each of these inital values randomly selected from NASS distributions
AgentData = {
        "AgeInit" : int(45.0),
        "nFields" : 1,
        "AreaFields" : np.array([10]),
        "LandStatus" : 0,
        "density" : 2,
        }

AgentArray, dFASM = init.InitializeDomain(Ny,Nx)
AgentArray = init.PlaceAgents(AgentArray, lc, dist2city)
dFASM = init.InitializeAgents(AgentArray, AgentData, dFASM, dist2city, Ny, Nx)

#---------------------------------------
#loop through decision process - change into function?
#---------------------------------------


for i in np.arange(1,Nt):
    for j in np.arange(Nx):
        for k in np.arange(Ny):
            
            cell_coord = j*Ny + k
            
            Profit_ant_ij = Profit_ant[i-1,j,k]
            Profit_p      = P[cell_coord][i,:].reshape((Nc,1))
    
            # Existing Crop ID
            CurCropChoice = CropID_all[i-1,j,k]
            CurCropChoice_ind = CurCropChoice.astype('int') - 1
            
            #Crop Decider
            CropChoice, ProfitChoice = cd.DecideN(a_ra, b_ra, fmin, fmax, n, Profit_ant_ij, CropIDs, \
                Profit_p, rule=True)
            
            # Check if return  values indicate the farmer shouldn't switch
            #seems like this could either be part of the above function or a new one?
            if(CropChoice==-1) and (ProfitChoice==-1):
                CropID_all[i,j,k] = CropID_all[i-1,j,k]
                Profit_ant[i,j,k] = P[j][i,CurCropChoice_ind]
                Profit_act[i,j,k] = Profit_ant[i,j,k] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1,1))
            else: #switch to the new crop
                CropID_all[i,j,k] = CropChoice
                Profit_ant[i,j,k] = ProfitChoice
                Profit_act[i,j,k] = Profit_ant[i,j,k] + np.random.normal(loc=0.0, scale=1000.0, size=(1,1,1))

            
         #update distance to city   
            
#Update AgentArray 
#where in the model does the code denote that the agent goes from farmer to urban or visa versa
     #dFASM[i][j].SwapAgent('aFarmer','aUrban',fromIndex,AgentArray)
        
temp_lc= lc #output of decision process

#write landcover to array - sub w Jons work
saveLC(temp_lc, 2010, it, DataPath)
           

#---------------------------------------
#update statistics  
#---------------------------------------

#update distance to city for new landcover
dist2city=minDistCity(temp_lc)
       
for i in np.arange(Ny):
 	for j in np.arange(Nx):
         if(AgentArray[i][j]=='aFarmer'):            
             dFASM[i][j].FarmAgents[0].UpdateAge()
             dFASM[i][j].FarmAgents[0].UpdateDist2city(dist2city[i][j])
      
        

#myF1 = farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 1) #where does farmer() come from??
#myF2 = farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 2)

#for t in np.arange(Nt,dtype=int):
    

   # DeltaDistToCity = ((-0.1 - -0.2)*np.random.random() - 0.2)    
   #OnFI_gr = 1.0 + OnFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)    
    #OffFI_gr = 1.0 + OffFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)

    #myF1.UpdateAge()
    #myF1.UpdateDistFromCity(DeltaDistToCity) # change this based on minDist coverage
    #myF1.UpdateOnFarmIncome(scale=OnFI_gr) #how does this work if the OnFI_gr comes after?
    #myF1.UpdateOffFarmIncome(scale=OffFI_gr)

    #DeltaDistToCity = ((-0.1 - -0.2)*np.random.random() - 0.2)    
    #OnFI_gr = 1.0 + OnFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)    
    #OffFI_gr = 1.0 + OffFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)
    
    #myF2.UpdateAge()
    #myF2.UpdateDistFromCity(DeltaDistToCity)
    #if(t==10):
     #   myF2.UpdateOnFarmIncome(loc=20000)        
    #else:
     #   myF2.UpdateOnFarmIncome(scale=OnFI_gr)
    #myF2.UpdateOffFarmIncome(scale=OffFI_gr)

