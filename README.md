# IM3-BoiseState

# GIS Analysis

## CDL Analysis
Order of operations

1. cdl2gcam - converts from cdl categories to GCAM SRP categories using a csv lookup, calculates area wieghted price and yeild based on 2010 NASS values (CDL2GCAM_SRP_price_yield.csv)
2. Aggregate GCAM grids - currently set to aggregate from 30m to 3km using the mode

Zonal Stats calculates the Shannon Diversity Index of 30m CDL data within each 1km/3km grid cell

## Spatial Initialization
getGISdata - functions getGISextent, getGCAM, 

## geofxs
*will be further populated to preform various statistical analysis

minDistCity - takes a np array of SRP GCAM categories, returns np arry of distances to closest city cell
