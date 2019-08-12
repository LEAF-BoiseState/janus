# IM3-BoiseState

# GIS Analysis

## CDL Analysis
Order of operations

1. cdl2gcam - converts from cdl categories to GCAM SRP categories using a csv lookup, calculates area wieghted price and yeild based on 2010 NASS values (CDL2GCAM_SRP_price_yield.csv)
2. Aggregate GCAM grids - currently set to aggregate from 30m to 3km using the mode

Zonal Stats calculates the Shannon Diversity Index of 30m CDL data within each 1km/3km grid cell

## Spatial Initialization

## getGISdata 
functions getGISextent, getGCAM, 
To add: pull physiographic information, re-grid, save

## geofxs
*will be further populated to preform various statistical analysis

minDistCity - takes a np array of SRP GCAM categories, returns np arry of distances to closest city cell
added saveLC - save the landcover of a given year to a labeled npy file 


# ABM Development
## Classes:
aFarmer - (a= agent) sets up farmer class with details on atrributes and functions of farmer 
dCell- (d = domain) - pixel with geographic information about terrain, and which agents are located


## Crop functions:
ReadCropCycle - this allows for multiple crops to be planted in a year, requires crop specific information for planting/growing/harvesting. This could call in CropModule for details on prices etc. We should rename the latter to be more cleat

CreateFASMdomain 

# LULCC ABM V.0

# 0. Declare some key variables
  -? Name of spatial domain map with LULCC classes   
  -? Name of spatial domain map with active/inactive cells (e.g., national forests, etc.)
  -? Name of spatial domain map of urban expansion areas
  -? Name of spatial domain map of any ag attributes needed (e.g., type of ag - leased etc.)
  - Number of simulation years or time steps  - done
  - Output interval - done
  - Output base name

# 1. Preprocessing
  - Load spatial maps
  - Initialize crops
  - Initialize profits
  - Initialize agents -- there are multiple steps here, how to streamline w functions?
  - Create any temporary, derived spatial domains (e.g. distance to city)
  -? Create storage containers for LULCC simulations (NaNs outside active domain?)
  - Create any exogenous agent types needed (e.g., regulators, global markets)

# 2. Simulation loop
  - Loop through time
     > Do any needed statistics at the beginning of time (i.e., update neighborhood stats for farmers, urban areas, etc.)
     > Get any new global info needed (i.e., value of crops)
     > Have all farmers decide on their crop choice for next year
     > Switch to new crops, update npy.
     
     >>> FUTURE VERSION 
        - Compute happiness metric based on urbanness, global crop price
        - Unhappy agents:
            > If in urban expansion zone, choose between: stay, sell, switch to corporate
            > If not in urban expansion zone, choose between: stay, sell (exurb), switch to corporate 
     > Decrement urban types depending on number of farmers that sell
     > Decrement exurban types developing on number of farmers that sell
     > Urban fraction inside development zone > threshold?
         - Yes: expand urban zone to accommodate 20 years' growth (this actually comes from COMPASS)
         - No: Do nothing
     > Add new urban types for next year
     > Add new exurban types for next year

# 3. Save output
   - Aggregate statistics through time (csv or NetCDF)
   - Spatial land use patterns through time (NetCDF)

