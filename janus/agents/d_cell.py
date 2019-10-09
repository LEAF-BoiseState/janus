import janus.agents.urban as urban_class
import janus.agents.farmer as farmer_class


class Dcell:
    """TODO: need class description

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
