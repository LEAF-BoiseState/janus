# Author: Jonathan Carvajal
# Date: 8/13/2019
# FileName: farmer.py
# Purpose: Holds definition of farmer


class Farmer:

    def __init__(self, **kwargs):
        self.Age = kwargs.get('Age')
        self.Dist2city = kwargs.get('Dist2city')

        self.LandStatus = kwargs.get('LandStatus')
        self.LandStatus = self.LandStatus

        # TODO initialize location (x, y)
        # note the LandStatus -- why is it that some are like that

        self.AgentID = kwargs.get('AgentID')
        self.AgentID = self.AgentID # unsure if needed
        
        self.LocationID = kwargs.get('LocationID')
        self.LocationID = self.LocationID
   
        self.nFields = kwargs.get('nFields')
        self.nFields = self.nFields

        self.alpha = kwargs.get('alpha')
        self.beta = kwargs.get('beta')

    def update_age(self):
        self.Age += 1

    def update_dist2city(self, new_dist):
        self.Dist2city = new_dist

    def update_switch(self):
        self.alpha += 0.1
        self.beta -= 0.01
