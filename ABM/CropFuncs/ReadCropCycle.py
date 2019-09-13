#==================================================================================#
#                                                                                  #
#                                                                                  #
#==================================================================================#
import numpy as np
import sys

FieldOps_nMonths = 12
FieldOps_nCols = 6
FieldOps_nRows = 12

#defines how agent is operating field; for each month what is being grown, vector of 1/0 did you plant, irrigate or harvest

class FieldOpsStruct:
	def __init__(self,Description,CropID,flagPlant,flagDevelop,flagIrrigate,flagHarvest):

		assert CropID.size       == FieldOps_nMonths, "CropID must be a vector of "+str(FieldOps_nMonths)
		assert flagPlant.size    == FieldOps_nMonths, "flagPlant must be a vector of "+str(FieldOps_nMonths)
		assert flagDevelop.size  == FieldOps_nMonths, "flagDevelop must be a vector of "+str(FieldOps_nMonths)
		assert flagIrrigate.size == FieldOps_nMonths, "flagIrrigate must be a vector of "+str(FieldOps_nMonths)
		assert flagHarvest.size  == FieldOps_nMonths, "flagHarvest must be a vector of "+str(FieldOps_nMonths)

		self.Description  = Description
		self.CropID       = CropID
		self.flagPlant    = flagPlant
		self.flagDevelop  = flagDevelop
		self.flagIrrigate = flagIrrigate
		self.flagHarvest  = flagHarvest


def ReadFieldOps(ReadPath,ReadFile):

	try:
		ifid = open(ReadPath+ReadFile,'r')
		Description = ifid.readline()
		lhs, rhs = Description.split("=",1)
		assert lhs == 'description', "FieldOps ERROR]: FieldOps description must be formatted as description='text'"
		Description = rhs.rstrip()
	except IOError:
		print('Cannot open file '+ReadPath+ReadFile)
		sys.exit()
	finally:
		ifid.close()

	Ops = np.loadtxt(ReadPath+ReadFile,delimiter=',',skiprows=2)
	
	# Parse ops... need new function, return structure
	FieldOps = ParseOpsArray(Ops,Description)

	return FieldOps;
#==================================================================================#
#                                                                                  #
#                                                                                  #
#==================================================================================#
def ParseOpsArray(Ops,Description):

	assert Ops.shape == (FieldOps_nRows,FieldOps_nCols), "[FieldOps ERROR]: FieldOps data file must begin with 2 header rows followed by 12 rows by 5 columns of data"

	Months       = Ops[:,0]
	CropID       = Ops[:,1]
	flagPlant    = Ops[:,2] 
	flagDevelop  = Ops[:,3]
	flagIrrigate = Ops[:,4]
	flagHarvest  = Ops[:,5]

	# Unit tests:
	assert np.array_equal(Months,np.linspace(1,12,num=12)), "[FieldOps ERROR] Months in FieldOps data array must be sequential from 1 to 12"

	assert np.array_equal(flagPlant, flagPlant.astype(bool)), "[FieldOps ERROR]: flagPlant must be 0 or 1"
	assert np.array_equal(flagDevelop, flagDevelop.astype(bool)), "[FieldOps ERROR]: flagDevelop must be 0 or 1"
	assert np.array_equal(flagIrrigate, flagIrrigate.astype(bool)), "[FieldOps ERROR]: flagIrrigate must be 0 or 1"
	assert np.array_equal(flagHarvest, flagHarvest.astype(bool)), "[FieldOps ERROR]: flagHarvest must be 0 or 1"

	FieldOps = FieldOpsStruct(Description,CropID,flagPlant,flagDevelop,flagIrrigate,flagHarvest)

	return FieldOps;

