# IM3-BoiseState

## CDL Analysis
Order of operations

1. cdl2gcam - converts from cdl categories to GCAM SRP categories using a csv lookup, calculates area wieghted price and yeild based on 2010 NASS values (CDL2GCAM_SRP_price_yield.csv)
2. Aggregate GCAM grids - currently set to aggregate from 30m to 3km using the mode

## Spatial Initialization

## geofxns
grid2poly - creates a matrix of polygons from a raster 
getGISextent - clips the output of the above polygon to the counties of interest
getGCAM - clips the landcover data (in this case GCAM, could re-name to lc) to the counties at scale of interest

minDistCity - takes a np array of *SRP GCAM* categories, returns np array of distances to closest city cell **this will need to be edited to take whichever landcover is being used**
To add: pull physiographic information, re-grid, save

## getGISdata 
select counties, year, and scale of interest to return the extent and inital gcam coverage


# Model Structure
The model is ... based on cells and classes ...

## Classes:
aFarmer - (a= agent) sets up farmer class with details on atrributes and functions of farmer 
dCell- (d = domain) - pixel with geographic information about terrain, and which agents are located

## Crop functions:
ReadCropCycle - this allows for multiple crops to be planted in a year, requires crop specific information for planting/growing/harvesting. This could call in CropModule for details on prices etc. We should rename the latter to be more clear

# LULCC ABM V.0

# 0. Declare key variables
  - Number of simulation years or time steps
  - Agent attributes regarding switching crops
  - Max/min (total profit or percentage?)
  - Output base name??

# 1. Preprocessing
  - Load spatial maps
  - Initialize crops
  - Initialize profits
  - Initialize agents
  - Create any temporary, derived spatial domains (e.g. distance to city)
  -? Create storage containers for LULCC simulations (NaNs outside active domain?)
  -? Create any exogenous agent types needed (e.g., regulators, global markets)

# 2. Simulation loop
  - Loop through time
     - Compute statistics at the beginning of time (i.e., update neighborhood stats for farmers, urban areas, etc.)
     - Get any new global info needed (i.e., value of crops)
     - Have all farmers decide on their crop choice for next year
    

# 3. Update Variables
   - Switch to new crops, update npy.
   - Update agent ages

# 4. Save output
   - Aggregate statistics through time
   - Spatial land use patterns through time 

## Post Processing

Zonal Stats calculates the Shannon Diversity Index of 30m CDL data within each 1km/3km grid cell
