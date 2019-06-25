# Outline of algorithm...

# 0. Declare some key variables
#   - Name of spatial domain map with LULCC classes 
#   - Name of spatial domain map with active/inactive cells (e.g., national forests, etc.)
#   - Name of spatial domain map of urban expansion areas
#   - Name of spatial domain map of any ag attributes needed (e.g., type of ag - leased etc.)
#   - Number of simulation years or time steps
#   - Output interval
#   - Output base name

# 1. Preprocessing
#   - Load spatial maps
#   - Set up any agent classes for spatial domains
#   - Create any temporary, derived spatial domains
#   - Create storage containers for LULCC simulations (NaNs outside active domain?)
#   - Create any exogenous agent types needed (e.g., regulators, global markets)

# 2. Simulation loop
#   - Loop through time
#       > Do any needed statistics at the beginning of time (i.e., update neighborhood stats for farmers, urban areas, etc.)
#       > Get any new global info needed (i.e., value of crops, number of potential developers in reservoir)
#       > Get all farmer types
#           - Compute happiness metric based on urbanness, global crop price
#           - Unhappy agents:
#               > If in urban expansion zone, choose between: stay, sell, switch to corporate
#               > If not in urban expansion zone, choose between: stay, sell (exurb), switch to corporate 
#       > Decrement urban types depending on number of farmers that sell
#       > Decrement exurban types developing on number of farmers that sell
#       > Urban fraction inside development zone > threshold?
#           - Yes: expand urban zone to accommodate 20 years' growth (this actually comes from COMPASS)
#           - No: Do nothing
#       > Add new urban types for next year
#       > Add new exurban types for next year

# 3. Save output
#   - Aggregate statistics through time (csv or NetCDF)
#   - Spatial land use patterns through time (NetCDF)


import geopandas as gp
import numpy as np
from geofxns import minDistCity #slow
import matplotlib.pyplot as plt
import Classes.aFarmer as farmer
import Classes.dCellClass as cell

DataPath= '/Users/kek25/Documents/GitRepos/IM3-BoiseState/'

#load extent
extent=gp.read_file(DataPath + 'ABMdev/Data/extent_1km_AdaCanyon.shp')
#load inital landcover
lc=np.load(DataPath + 'ABMdev/Data/gcam_1km_2010_AdaCanyon.npy')
#initalize minimum distance to city
dist2city=minDistCity(lc)

nRows, nCols = lc[0].shape
Nt=20

#setup grid space for agent locations
AgentArray = np.empty((nRows,nCols),dtype='U10')
dFASM = np.empty((nRows,nCols), dtype=object) #domain 

for i in np.arange(nRows):
	for j in np.arange(nCols):
		dFASM[i][j] = cell.dCellClass()


#Update so each of these inital values randomly selected from NASS distributions
#Initialize farmer
AgeInit = int(45.0)
nFields=1
AreaFields=np.array([10])
LandStatus=0


#assign agents on the landscape
AgentArray[np.logical_and(lc[0] > 0, lc[0] <28)] = 'aFarmer'
AgentArray[np.logical_or(lc[0] == 28, lc[0] == 23)] ='water' #somehow with the reclassification, a bunch of edge cells are labled as water??
AgentArray[dist2city == 0] = 'aUrban'
AgentArray[np.logical_or(lc[0] == 24, lc[0] == 21)] = 'empty' #RockIceDesert, Shrubland
AgentArray[np.logical_or(lc[0] == 19, lc[0] == 15)] = 'empty' #forest, pasture


for i in np.arange(nRows):
 	for j in np.arange(nCols):
         if(AgentArray[i][j]=='aFarmer'):
             NewAgent = farmer.aFarmer(AgeInit, nFields, AreaFields, LandStatus, dist2city[i][j])
             dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
            

            
#loop
#update statistics         
        
        #use the update age function
        #update distance to city from minDist layer
        