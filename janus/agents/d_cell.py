import janus.agents.urban as urban_class
import janus.agents.farmer as farmer_class


class Dcell:
    """A class that contains both static and dynamic information about the simulation domain

    :param Area: The area of the cell
    :param cLat: The latitude of the cell center
    :param cLon: The longitude of the cell center
    :param Elev: The elevation of the cell
    :param Slope: The slope of the cell
    :param Aspect: The aspect of the cell
    :param perSand: The soil percent sand
    :param perSilt: The soil percent silt
    :param perClay: The soill percent clay
    :param nUrbAgent: The number of urban agents in the cell (initialized to 0)
    :param nFarmAgent: The number of farmer agents in the cell (initialized to 0)
    :param UrbanAgents: An empty container in which to store UrbanAgent class types
    :param FarmerAgents: An empty container in which to store FarmerAgent class types
        
        

    """
    def __init__(self, **kwargs):
        self.Area = kwargs.get('Area')
        self.cLat = kwargs.get('cLat')
        self.cLon = kwargs.get('cLon')
        self.Elev = kwargs.get('Elev')
        self.Slope = kwargs.get('Slope')
        self.Aspect = kwargs.get('Aspect')
        self.perSand = kwargs.get('perSand')
        self.perSilt = kwargs.get('perSilt')
        self.perClay = kwargs.get('perClay')
        self.nUrbAgent = 0
        self.nFarmAgent = 0
        self.UrbanAgents = []
        self.FarmerAgents = []

    def add_agent(self, agent_struct):
        """Adds a new agent to a list
        pre: agentStruct has been instantiated with init.Agents and is a valid agent type
        post: agent has been added to an array

        :param agent_struct:

        :return:

        """
        agent_type = type(agent_struct).__name__

        if agent_type == urban_class.Urban.__name__:
            self.nUrbAgent += 1
            self.UrbanAgents.append(agent_struct)

        if agent_type == farmer_class.Farmer.__name__:
            self.nFarmAgent += 1
            self.FarmerAgents.append(agent_struct)
