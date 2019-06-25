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
lc=lc.squeeze()
nRows, nCols = lc.shape
Nt=20

#setup grid space for agent locations
AgentArray = np.empty((nRows,nCols),dtype='U10')
dFASM = np.empty((nRows,nCols), dtype=object) #domain 

for i in np.arange(nRows):
	for j in np.arange(nCols):
		dFASM[i][j] = cell.dCellClass()


#each of these inital values randomly selected from NASS distributions
#Initialization values
AgeInit = 45.0
DistFromCityInit = 20.0
OnFIInit = 45000.0
OffFIInit = 20000.0
CropIDInit = 1

#initalize farmer
nFields=1 
AreaFields=10 
LandStatus=0

#loop
#update statistics
#update minimum distance to city
dist2city=minDistCity(lc)

#assign agents on the landscape
AgentArray[np.logical_and(lc > 0, lc <28)] = 'aFarmer'
AgentArray[np.logical_or(lc == 28, lc == 23)] ='water' #somehow with the reclassification, a bunch of edge cells are labled as water??
AgentArray[dist2city == 0] = 'aUrban'
AgentArray[np.logical_or(lc == 24, lc == 21)] = 'empty' #RockIceDesert, Shrubland
AgentArray[np.logical_or(lc == 19, lc == 15)] = 'empty' #forest, pasture


for i in np.arange(nRows):
 	for j in np.arange(nCols):
		
 		if(AgentArray[i][j]=='aFarmer'):
 			NewAgent = farmer.aFarmer(AgeInit, nFields, AreaFields, LandStatus)
	 		#what is happening here?
 		dFASM[i][j].AddAgent(AgentArray[i][j], NewAgent)
         
        
        #Farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 1)
    
        #assign farmer ages
        #use the update age function
        #assign distance to city from minDist layer
        
myF1 = farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 1)
myF2 = farmer(AgeInit, DistFromCityInit, OnFIInit, OffFIInit, 2)

for t in np.arange(Nt,dtype=int):
    

    DeltaDistToCity = ((-0.1 - -0.2)*np.random.random() - 0.2)    
    OnFI_gr = 1.0 + OnFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)    
    OffFI_gr = 1.0 + OffFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)

    myF1.UpdateAge()
    myF1.UpdateDistFromCity(DeltaDistToCity)
    myF1.UpdateOnFarmIncome(scale=OnFI_gr)
    myF1.UpdateOffFarmIncome(scale=OffFI_gr)

    DeltaDistToCity = ((-0.1 - -0.2)*np.random.random() - 0.2)    
    OnFI_gr = 1.0 + OnFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)    
    OffFI_gr = 1.0 + OffFI_agr*((2.0 - -1.0)*np.random.random() + -1.0)
    
    myF2.UpdateAge()
    myF2.UpdateDistFromCity(DeltaDistToCity)
    if(t==10):
        myF2.UpdateOnFarmIncome(loc=20000)        
    else:
        myF2.UpdateOnFarmIncome(scale=OnFI_gr)
    myF2.UpdateOffFarmIncome(scale=OffFI_gr)