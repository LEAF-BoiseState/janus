import numpy as np


class FieldOpsStruct:
	"""Defines how agent is operating field; for each month what is being grown,
	vector of 1/0 did you plant, irrigate or harvest.

	"""
	FIELDOPS_NMONTHS = 12
	FIELDOPS_NCOLS = 6
	FIELDOPS_NROWS = 12

	def __init__(self, Description, CropID, flagPlant, flagDevelop, flagIrrigate, flagHarvest):

		assert CropID.size == FieldOpsStruct.FIELDOPS_NMONTHS, "CropID must be a vector of {}.".format(FieldOpsStruct.FIELDOPS_NMONTHS)
		assert flagPlant.size == FieldOpsStruct.FIELDOPS_NMONTHS, "flagPlant must be a vector of {}.".format(FieldOpsStruct.FIELDOPS_NMONTHS)
		assert flagDevelop.size == FieldOpsStruct.FIELDOPS_NMONTHS, "flagDevelop must be a vector of {}.".format(FieldOpsStruct.FIELDOPS_NMONTHS)
		assert flagIrrigate.size == FieldOpsStruct.FIELDOPS_NMONTHS, "flagIrrigate must be a vector of {}.".format(FieldOpsStruct.FIELDOPS_NMONTHS)
		assert flagHarvest.size == FieldOpsStruct.FIELDOPS_NMONTHS, "flagHarvest must be a vector of {}.".format(FieldOpsStruct.FIELDOPS_NMONTHS)

		self.Description = Description
		self.CropID = CropID
		self.flagPlant = flagPlant
		self.flagDevelop = flagDevelop
		self.flagIrrigate = flagIrrigate
		self.flagHarvest = flagHarvest


def read_field_ops(ReadPath, ReadFile):
	"""

	:param ReadPath:
	:param ReadFile:

	:return:

	"""

	try:
		ifid = open(ReadPath+ReadFile,'r')
		Description = ifid.readline()
		lhs, rhs = Description.split("=",1)
		assert lhs == 'description', "FieldOps ERROR]: FieldOps description must be formatted as description='text'"
		Description = rhs.rstrip()

	except IOError:
		raise IOError('Cannot open file '+ReadPath+ReadFile)

	finally:
		ifid.close()

	Ops = np.loadtxt(ReadPath+ReadFile,delimiter=',',skiprows=2)

	# Parse ops... need new function, return structure
	FieldOps = ParseOpsArray(Ops,Description)

	return FieldOps


def parse_ops_array(Ops, Description):

	assert Ops.shape == (FieldOpsStruct.FIELDOPS_NROWS, FieldOpsStruct.FIELDOPS_NCOLS), "[FieldOps ERROR]: FieldOps data file must begin with 2 header rows followed by 12 rows by 5 columns of data"

	Months = Ops[:, 0]
	CropID = Ops[:, 1]
	flagPlant = Ops[:, 2]
	flagDevelop = Ops[:, 3]
	flagIrrigate = Ops[:, 4]
	flagHarvest = Ops[:, 5]

	assert np.array_equal(Months,np.linspace(1, 12, num=12)), "[FieldOps ERROR] Months in FieldOps data array must be sequential from 1 to 12"

	assert np.array_equal(flagPlant, flagPlant.astype(bool)), "[FieldOps ERROR]: flagPlant must be 0 or 1"
	assert np.array_equal(flagDevelop, flagDevelop.astype(bool)), "[FieldOps ERROR]: flagDevelop must be 0 or 1"
	assert np.array_equal(flagIrrigate, flagIrrigate.astype(bool)), "[FieldOps ERROR]: flagIrrigate must be 0 or 1"
	assert np.array_equal(flagHarvest, flagHarvest.astype(bool)), "[FieldOps ERROR]: flagHarvest must be 0 or 1"

	FieldOps = FieldOpsStruct(Description,CropID,flagPlant,flagDevelop,flagIrrigate,flagHarvest)

	return FieldOps
