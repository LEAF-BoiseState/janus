"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""
#---------------------------------------
#  Load Packages
#---------------------------------------
import numpy as np
import os

userPath='/Users/kek25/Documents/GitRepos/'
os.chdir(userPath+'IM3-BoiseState/ABM')

import PreprocessingTools.geofxns as gf
import CropFuncs.CropDecider as cd
import InitializeAgentsDomain as init
import PostProcessing.FigureFuncs as ppf
import PreprocessingTools.getNASSAgentData as getNASS
DataPath= userPath+'IM3-BoiseState/Data/'
GCAMpath=DataPath+'GCAM/'

import geopandas as gp
counties_shp= gp.read_file(DataPath+'Counties/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')
key_file= gp.read_file(DataPath+'CDL2GCAM_SRP_categories.csv', sep=',')

#---------------------------------------
# 0. Declare Variables
#---------------------------------------
Nt = 50
#set agent attributes: list of switching parameters (alpha, beta)
switch = [[4.5, 1.0], #switching averse
          [0.5, 3.0]] #switching tolerant


#Max and min .... total Profit, percent profit?
fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100

cd.DefineSeed(5)
#---------------------------------------
# 1. Initialize Landscape and Domain
#---------------------------------------

countyList=['Ada', 'Canyon']  
year=2010
scale=3000 #scale of grid in meters

#select initial gcam data from inital year 
lc=gf.getGCAM(counties_shp, countyList, year, scale, GCAMpath)

#initalize minimum distance to city
dist2city=gf.minDistCity(lc)

Ny, Nx = lc[0].shape

domain = init.InitializeDomain(Ny, Nx)
#---------------------------------------
#  Initialize Crops
#---------------------------------------
Nc = 4 #there are actually 17 when the 1km is run, need random profit profiles for each of these 
CropIDs =np.array([1,2,3,10]) # need to make this automatic depending on which crops show up (which of AllCropIDs == np.unique(lc))
CropIDs= CropIDs.reshape((Nc,1))
#CropIDs=np.arange(Nc).reshape((Nc,1)) + 1
CropID_all = np.zeros((Nt,Ny,Nx))
CropID_all[0,:,:] = lc #this will be added into the cell class

#---------------------------------------
#  Initialize Profits
#---------------------------------------
Profit_ant = np.zeros((Nt,Ny,Nx))
Profit_act = np.zeros((Nt,Ny,Nx))

Profit_ant[0,:,:] = 30000.0 + np.random.normal(loc=0.0,scale=1000.0,size=(1,Ny,Nx))
Profit_act[0,:,:] = Profit_ant[0,:,:]

Profits = [] # A list of numpy arrays that will be Nt x Nc 
Profits = cd.GeneratePrices(Nt)
Profits = Profits[:, 0:Nc]
#Profits = Profits[:, 2:6] The choice of crop profits will completely drive the outcome ... how do we use that?
#---------------------------------------
#  Initialize Agents
#---------------------------------------

variables=["TENURE", "AREA OPERATED"]
NASS_yr=2007 #2007, 2012 are available 

tenure=getNASS.TenureArea(countyList, NASS_yr, variables) #tenure from individual counties could also be used 
ages=getNASS.Ages(NASS_yr)

AgentArray = init.PlaceAgents(Ny, Nx, lc, key_file, 'SRB') 
#this is where it breaks
domain = init.InitializeAgents(AgentArray, domain, dist2city, tenure, ages, switch, Ny, Nx) 

#---------------------------------------
# 2. loop through decision process 
#---------------------------------------


for i in np.arange(1,Nt):
    
    for j in np.arange(Ny):
        for k in np.arange(Nx):
            #Assess Profit
            Profit_last, Profit_pred = cd.AssessProfit(CropID_all[i-1,j,k], Profits[i-1,:], Profits[i,:], Nc, CropIDs)
            #Decide on Crop
            "this needs to call alpha/beta from the agent in that cell"
            CropChoice, ProfitChoice = cd.DecideN(a_ra, b_ra, fmin, fmax, n, Profit_last, CropIDs, \
                                                      Profit_pred, rule=True)
            CropID_all, Profit_ant, Profit_act = cd.MakeChoice(CropID_all, Profit_last, Profit_pred, \
                                                               CropChoice, ProfitChoice, Profit_act, i,j,k) #"move these indicies into the input variables"
            CropChoice, ProfitChoice = cd.DecideN(a_ra, b_ra, fmin, fmax, n, Profit_last, CropIDs, \
                                                      Profit_pred, rule=True)
            CropID_all[i,j,k], Profit_ant[i,j,k], Profit_act[i,j,k] = cd.MakeChoice(CropID_all[i-1,j,k], Profit_last, Profit_ant, \
                                                               CropChoice, ProfitChoice, seed = False) #is there a way to set this up so you can pass a NULL value or no value when seed=False?
 
ppf.CropPerc(CropID_all, CropIDs, Nt, Nc)
#ppf.CreateAnimation(CropID_all, Nt)
#CropID_all, Profit_ant, Profit_act = cd.MakeDecision(Nt, Ny, Nx, Nc, CropID_all, Profits, Profit_ant, Profit_act, a_ra, b_ra, fmin, fmax, n, CropIDs)
#"one unit test would be to confirm that non-ag stayed the same and that all of the ag did not stay the same"        
#need to pull out the parts that dont rely on the loop and put the decision inside of it, that way relevant info can be updated between timesteps; 

#---------------------------------------
# 3. update variables 
#---------------------------------------

#update distance to city from output of decision process - IF we were incorperating the urban agent then this would happen in each time step
#dist2city=minDistCity(lc_new) 
     
  #Update AgentArray 
#where in the model does the code denote that the agent goes from farmer to urban or visa versa
     #domain[i][j].SwapAgent('aFarmer','aUrban',fromIndex,AgentArray) "switch for now"
     
for i in np.arange(Ny):
 	for j in np.arange(Nx):
         if(AgentArray[i][j]=='aFarmer'):            
             domain[i][j].FarmAgents[0].UpdateAge()
             domain[i][j].FarmAgents[0].UpdateDist2city(dist2city[i][j])
      
#---------------------------------------
# 4. Save Output
#---------------------------------------
      
#write landcover to array - sub w Jons work
#saveLC(temp_lc, 2010, it, DataPath)
           

