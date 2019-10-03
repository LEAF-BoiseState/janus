"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""
#---------------------------------------
#  Load Packages
#---------------------------------------
import os

userPath='/Users/kek25/Documents/GitRepos/'
os.chdir(userPath+'IM3-BoiseState/ABM')

import numpy as np
import PreprocessingTools.geofxns as gf
import CropFuncs.CropDecider as cd
import InitializeAgentsDomain as init
import PostProcessing.FigureFuncs as ppf
import PreprocessingTools.getNASSAgentData as getNASS
import geopandas as gp
import pandas as pd

DataPath= userPath+'IM3-BoiseState/Data/'
GCAMpath=DataPath+'GCAM/'


counties_shp= gp.read_file(DataPath+'Counties/Counties_SRB_clip_SingleID.shp')
counties_shp=counties_shp.set_index('county')
key_file= pd.read_csv(DataPath+'CDL2GCAM_SRP_categories.csv', sep=',')
# TODO: add path to profit_file csv from config file and the ResultsPath for saving
profit_file=pd.read_csv(userPath+'IM3-BoiseState/ABM/PreprocessingTools/GenerateSyntheticPrices_test_output.csv', header=None)


ResultsPath=DataPath+'Results/'

#---------------------------------------
# 0. Declare Variables
#---------------------------------------
Nt = 20
#set agent switching parameters (alpha, beta)
switch = np.array([[4.5, 1.0], #switching averse
                   [0.5, 3.0]]) #switching tolerant
#proportion of each switching type, lower than p is averse, higher is tolerant
p=0.5 

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

#ID crops based on those in the initial land cover
# TODO: make sure that this key_file is being called to properly from config
ag=np.where(key_file['SRB_cat'] == 'ag')
CropIDs =np.int64(key_file['SRB_GCAM_id_list'][ag[0]])
Num_crops = len(CropIDs)
CropIDs =CropIDs.reshape(Num_crops,1)

CropID_all = np.zeros((Nt,Ny,Nx))
CropID_all[0,:,:] = lc #this will be added into the cell class

#---------------------------------------
#  Initialize Profits
#---------------------------------------
# initializes profits based on profit signals from csv output from generate synthetic prices 
profit_signals=np.transpose(profit_file.as_matrix())
assert np.all([profit_signals[:,0], CropIDs[:,0]]), 'Crop IDs in profit signals do not match Crop IDs from landcover'
profit_signals = profit_signals[:,1:]
assert profit_signals.shape[1] == Nt, 'The number of timesteps in the profit signals do not match the number of model timesteps'
profits_actual =init.Profits(profit_signals, Nt, Ny, Nx, CropID_all, CropIDs)
            
#---------------------------------------
#  Initialize Agents
#---------------------------------------

variables=["TENURE", "AREA OPERATED"]
NASS_yr=2007 #2007, 2012 are available 
NASS_countyList=['ADA', 'CANYON']  #these have to be capitalized
tenure=getNASS.TenureArea('ID', NASS_countyList, NASS_yr, variables) #tenure from individual counties can also be used 
ages=getNASS.Ages(NASS_yr, 'ID')

AgeCDF=getNASS.makeAgeCDF(ages)
TenureCDF=getNASS.makeTenureCDF(tenure)

AgentArray = init.PlaceAgents(Ny, Nx, lc, key_file, 'SRB') 

domain = init.Agents(AgentArray, domain, dist2city, TenureCDF, AgeCDF, switch, Ny, Nx, lc, p) 

#---------------------------------------
# 2. loop through decision process 
#---------------------------------------

for i in np.arange(1,Nt):
    
    for j in np.arange(Ny):
        for k in np.arange(Nx):
            if domain[j,k].FarmerAgents:
                #Assess Profit
                profit_last, profit_pred = cd.AssessProfit(CropID_all[i-1,j,k], profits_actual[i-1,j,k], profit_signals[:,i], Num_crops, CropIDs)
                #Choose between crops 
                CropChoice, profitChoice = cd.DecideN(domain[j,k].FarmerAgents[0].alpha, domain[j,k].FarmerAgents[0].beta, fmin, fmax, n, profit_last, CropIDs, profit_pred, rule=True)
                #Decid whether to switch and add random variation to actual profit
                CropID_all[i,j,k], profits_actual[i,j,k] = cd.MakeChoice(CropID_all[i-1,j,k], profit_last, CropChoice, profitChoice, seed=False) 
                
                #update agent attributes
                domain[j,k].FarmerAgents[0].UpdateAge() #there is something wrong w this - they ballon up to 600 years
 


ppf.CropPerc(CropID_all, CropIDs, Nt, Num_crops, scale, ResultsPath, key_file, ag)
ppf.AgentAges(domain, AgentArray, Ny, Nx)

#---------------------------------------
# 3. Save output
#---------------------------------------

#save timeseries of landcover coverage
np.save(ResultsPath+'landcover_'+str(scale)+'m_'+str(Nt)+'yr', CropID_all)
# save timeseries of profits 
np.save(ResultsPath+'profits_'+str(scale)+'m_'+str(Nt)+'yr', profits_actual)
# save domain, can be used for initialization
np.save(ResultsPath+'domain_'+str(scale)+'m_'+str(Nt)+'yr', domain)

