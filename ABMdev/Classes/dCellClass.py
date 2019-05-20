#==================================================================================#
#                                                                                  #
#                                                                                  #
#==================================================================================#

class dCellClass:
	def __init__(self,**kwargs):
		self.Area       = kwargs.get('Area')
		self.cLat       = kwargs.get('cLat')
		self.cLon       = kwargs.get('cLon')
		self.Elev       = kwargs.get('Elev')
		self.Slope      = kwargs.get('Slope')
		self.Aspect     = kwargs.get('Aspect')
		self.perSand    = kwargs.get('perSand')
		self.perSilt    = kwargs.get('perSilt')
		self.perClay    = kwargs.get('perClay')
		self.nFarmAgent = 0
		self.nUrbAgent  = 0


	#==============================================================================#
	#                                                                              #
	#                                                                              #
	#==============================================================================#
	def AddAgent(self,agentType,AgentStruct):

		assert (agentType=="aUrban") or (agentType=="aFarmer"), "Agent type must either be aUrban or aFarmer"

		if(agentType=="aUrban"):
			# Check to see if there are currently no agents of this type in the cell. If true, 
			# initialize an empty list to store at least one
			if(self.nUrbAgent==0):
				self.UrbanAgents = []

			self.nUrbAgent += 1				
			self.UrbanAgents.append(AgentStruct)

		if(agentType=="aFarmer"):
			# Check to see if there are currently no agents of this type in the cell. If true, 
			# initialize an empty list to store at least one
			if(self.nFarmAgent==0):
				self.FarmAgents = []

			self.nFarmAgent += 1
			self.FarmAgents.append(AgentStruct)

	#==============================================================================#
	#                                                                              #
	#                                                                              #
	#==============================================================================#
	def SwapAgent(self,fromType,toType,fromIndex,toAgentStruct):
		
		#=====================#
		# Initial error traps #
		#=====================#
		assert (fromType=="aUrban") or (fromType=="aFarmer"), "Agent fromType must either be aUrban or aFarmer"
		assert (toType=="aUrban") or (toType=="aFarmer"), "Agent toType must either be aUrban or aFarmer"

		#=====================#
		# Remove fromAgent    #
		#=====================#
		if(fromType=="aUrban"):
			# Error trap that this type of agent exists
			assert self.nUrbAgent>0, "Trying to delete aUrban agent in cell where none exists"

			# Error trap that the provided index does not exceed the number of this agent type that exist in this cell
			assert fromIndex < self.nUrbAgent, "Trying to delete urban agent with out of bound index"

			# Delete the agent at index fromIndex
			del self.UrbanAgents[fromIndex]

			# Decrement agent counter
			self.nUrbAgent -= 1

		if(fromType=="aFarmer"):
			# Error trap that this type of agent exists
			assert self.nFarmAgent>0, "Trying to replace aFarmer agent in cell where none exists"

			# Error trap that the provided index does not exceed the number of this agent type that exist in this cell
			assert fromIndex < self.nFarmAgent, "Trying to delete aUrban agent in cell where none exists"

			# Delete the agent at index fromIndex
			del self.FarmAgents[fromIndex]

			# Decrement agent counter
			self.nFarmAgent -= 1

		#=====================#
		# Add toAgent         #
		#=====================#
		# This is just a function call to the above function
		self.AddAgent(toType,toAgentStruct)

	#==============================================================================#
	#                                                                              #
	#                                                                              #
	#==============================================================================#
	



