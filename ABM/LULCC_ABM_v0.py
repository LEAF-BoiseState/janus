"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""
#---------------------------------------
#  Load Packages
#---------------------------------------
import geopandas as gp
import numpy as np
import PreprocessingTools.geofxns as gf
import CropFuncs.CropDecider as cd
import InitializeAgentsDomain as init
import PostProcessing.FigureFuncs as ppf

userPath='~/Documents/GitRepos/'
DataPath= userPath+'IM3-BoiseState/Data/'

#---------------------------------------
# 0. Declare Variables
#---------------------------------------
#set agent attributes: switching parameters 
"These should be pulled from a distribution"
a_ra = 4.5
b_ra = 1.0

#Max and min .... total Profit, percent profit?
fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100

cd.DefineSeed(5)
#---------------------------------------
# 1. Initialize Landscape and Domain
#---------------------------------------
#load extent
extent=gp.read_file(DataPath + 'extent_3km_AdaCanyon.shp')
#load inital landcover
lc=np.load(DataPath + 'gcam_3km_2010_AdaCanyon.npy')
#initalize minimum distance to city
dist2city=gf.minDistCity(lc)

Ny, Nx = lc[0].shape
Nt = 50

dFASM = init.InitializeDomain(Ny, Nx) #rename dFASm
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
#  Initialize Agents Stub (e.g. not getting used)
#---------------------------------------
#Update so each of these inital values are randomly selected from NASS distributions
AgentData = {
        "AgeInit" : int(45.0),
        "LandStatus" : 0,
        "density" : 2,
        "alpha": a_ra,
        "beta": b_ra
        }
#we need to be able to associate alpha/beta parameters with each agent. 
AgentArray = init.PlaceAgents(Ny, Nx, lc, dist2city) 
#dFASM = init.InitializeAgents(AgentArray, AgentData, dFASM, dist2city, Ny, Nx) #this will be done in the agent factory - which is great cause it aint working right now

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
     #dFASM[i][j].SwapAgent('aFarmer','aUrban',fromIndex,AgentArray) "switch for now"
     
for i in np.arange(Ny):
 	for j in np.arange(Nx):
         if(AgentArray[i][j]=='aFarmer'):            
             dFASM[i][j].FarmAgents[0].UpdateAge()
             dFASM[i][j].FarmAgents[0].UpdateDist2city(dist2city[i][j])
      
#---------------------------------------
# 4. Save Output
#---------------------------------------
      
#write landcover to array - sub w Jons work
#saveLC(temp_lc, 2010, it, DataPath)
           

