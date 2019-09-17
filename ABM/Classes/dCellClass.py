from Classes.AgentFactory import AgentFactory

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
		self.agents = []

    #purpose: adds a new agent to a list
    #pre: agentStruct has been instantiated and is a valid agent type
    #post: agent has been added to an array
	def AddAgent(self,agentStruct):
		agentType = type(agentStruct).__name__
		column = AgentFactory.getColumnIndex(agentType)

		if (agentType == "aUrban"):
			self.UrbanAgents.append(agentStruct)
		else:
			self.FarmerAgents.append(agentStruct)

    #purpose: agent is swapped with a different agent type
    #pre: from type contains a valid agent type. from index and to index is valid. to agent struct has been instantiated
    #post: agent has been swapped with a different agent type
	def SwapAgent(self, fromType, fromIndex, toAgentStruct, toIndex):
		toAgentType = type(toAgentStruct).__name__

		# ensure agent type is valid
		self._ValidateAgentType(fromType)
		self._ValidateAgentType(toAgentType)

		#=====================#
		# Remove fromAgent    #
		#=====================#
		if(fromType == "aUrban"):
			# ensure agents exists
			assert len(self.UrbanAgents) > 0, "Trying to delete aUrban agent in cell where none exists"
			assert fromIndex < len(self.UrbanAgents), "Trying to delete urban agent with out of bound index"

			# Delete the agent at index fromIndex
			del self.UrbanAgents[fromIndex]
		else:
			# Error trap that this type of agent exists
			assert len(self.FarmerAgents) > 0, "Trying to replace aFarmer agent in cell where none exists"

			# Error trap that the provided index does not exceed the number of this agent type that exist in this cell
			assert fromIndex < len(self.FarmerAgents), "Trying to delete aUrban agent in cell where none exists"

			# Delete the agent at index fromIndex
			del self.FarmerAgents[fromIndex]

		#=====================#
		# Add toAgent         #
		#=====================#
		# This is just a function call to the above function
		self.AddAgent(toAgentStruct)

	#==============================================================================#
	#                                                                              #
	#                                                                              #
	#==============================================================================#
	def _ValidateAgentType(self,agentType):
		# ensure agent type is valid
		assert (agentType == "aUrban") or (agentType == "aFarmer"), "Agent fromType must either be aUrban or aFarmer"


