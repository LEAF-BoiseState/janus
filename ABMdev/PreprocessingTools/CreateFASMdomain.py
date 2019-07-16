#Functional Agent Simulater for MSD
import numpy as np
import Classes.dCellClass as cell


input_base = 'test_landscape/test_landscape_' #this will have base layers of landscape characteristics in it
input_ext = '.npy'

output_file = input_base+'domain.npy'

# Declare number of rows and columns
nRows = 40
nCols = 40

# Create a numpy array that is (nRows x nCols) and is of type "object"
dFASM = np.empty((nRows,nCols), dtype=object)
assert (dFASM.size==nRows*nCols), "Could not create domain"

# Load input files
gArea    = np.load(input_base+'area'+input_ext)
gAspect  = np.load(input_base+'asp'+input_ext)
gElev    = np.load(input_base+'elev'+input_ext)
gLat     = np.load(input_base+'lat'+input_ext)
gLon     = np.load(input_base+'lon'+input_ext)
gPerSand = np.load(input_base+'persand'+input_ext)
gPerSilt = np.load(input_base+'persilt'+input_ext)
gPerClay = np.load(input_base+'perclay'+input_ext)
gSlope   = np.load(input_base+'slp'+input_ext)

for i in np.arange(nRows):
	for j in np.arange(nCols):
		dFASM[i][j] = cell.dCellClass(Area=gArea[i][j],cLat=gLat[i][j],cLon=gLon[i][j],Elev=gElev[i][j],\
			Slope=gSlope[i][j],Aspect=gAspect[i][j],perSand=gPerSand[i][j],perSilt=gPerSilt[i][j],\
			perClay=gPerClay[i][j])

np.save(output_file,dFASM)
