#==================================================================================#
#                                                                                  #
# Create Test Landscape #
#                                                                                  #
#==================================================================================#
import numpy as np

output_base = 'test_landscape/test_landscape_'

nRows = 40
nCols = 40

cLat = 43.6150 	 # Boise latitude
cLon = -116.2023 # Boise longitude

delLat = 0.01 # Decimal degrees [approximate]
delLon = 0.01 # Decimal degrees [approximate]

Area = 1.0  # Area in km^2 

meanElev   = 824 # Boise elevation [m]
meanSlope  = 0.001 # Mean slope [m/m]
meanAspect = np.pi # Mean aspect [rad]

PerSand = 0.4
PerSilt = 0.4
PerClay = 0.2

assert (PerSand+PerSilt+PerClay)==1.0, "percent sand, silt, clay must sum to 1.0"

minLat = cLat - delLat*(nRows/2)
minLon = cLon - delLon*(nRows/2)

lat = np.linspace(minLat,minLat+nRows*delLat,num=nRows)
lon = np.linspace(minLon,minLon+nCols*delLon,num=nCols)

lat = np.reshape(lat,(nRows,1))
lon = np.reshape(lon,(1,nCols))

Lat = np.tile(lat,(1,nCols))
Lon = np.tile(lon,(nRows,1))

gArea = Area*np.ones((nRows,nCols))

gElev   = np.random.normal(loc=meanElev,scale=2.0,size=(nRows,nCols))
gSlope  = np.random.uniform(low=0.001*meanSlope,high=10*meanSlope,size=(nRows,nCols))
gAspect = np.random.uniform(low=0.5*meanAspect,high=2*meanAspect,size=(nRows,nCols))

gPerSand = PerSand*np.ones((nRows,nCols)) 
gPerSilt = PerSilt*np.ones((nRows,nCols))
gPerClay = PerClay*np.ones((nRows,nCols))

# Save outputs
np.save(output_base+'area.npy',gArea)
np.save(output_base+'lat.npy',Lat)
np.save(output_base+'lon.npy',Lon)
np.save(output_base+'elev.npy',gElev)
np.save(output_base+'slp.npy',gSlope)
np.save(output_base+'asp.npy',gAspect)
np.save(output_base+'persand.npy',gPerSand)
np.save(output_base+'persilt.npy',gPerSilt)
np.save(output_base+'perclay.npy',gPerClay)

