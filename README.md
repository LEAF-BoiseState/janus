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


# ABM Development
## Classes:
aFarmer - (a= agent) sets up farmer class with details on atrributes and functions of farmer 
dCell- (d = domain) - pixel with geographic information about terrain, and which agents are located


## Crop functions:
ReadCropCycle - this allows for multiple crops to be planted in a year, requires crop specific information for planting/growing/harvesting. This could call in CropModule for details on prices etc. We should rename the latter to be more cleat

CreateFASMdomain 
