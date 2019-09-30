# IM3-BoiseState

The Agent Based model was designed to simulate land cover changes over time. These landcover changes are carried out by individual agents that choose to either continue planting the same crop, or choose to switch to a new crop based on expected profits. 


# Model Structure
The model is ... based on cells and classes ...

dCell- (d = domain) - pixel with geographic information about terrain, and which agents are located

## Agents:
aFarmer:(a = agent) sets up farmer class with details on atrributes and functions of farmer 

aUrban: sets up urban class with attribute based on landcover classification of population density


# LULCC ABM V.0

# 0. Declare variables in config file
  - Number of simulation years or time steps
  - Agent attributes regarding switching crops
  - Max/min (total profit or percentage?)
 

# 1. Preprocessing
  - select counties, year, and scale of interest to return the extent and inital land cover numpy array
  - Initialize crops
  - Initialize profits
  - Initialize agents
  - Create any temporary, derived spatial domains (e.g. distance to city)

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
