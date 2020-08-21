# Author: Jonathan Carvajal
# Date: 8/13/2019
# FileName: farmer.py
# Purpose: Holds definition of farmer


class Farmer:

    def __init__(self,**kwargs):

        self.Age = kwargs.get('Age')
        self.Dist2city = kwargs.get('Dist2city')

        self.LandStatus = kwargs.get('LandStatus')
        self.LandStatus = self.LandStatus

        self.nFields = kwargs.get('nFields')
        self.nFields = self.nFields

        self.alpha = kwargs.get('alpha')
        self.beta = kwargs.get('beta')

        self.agentID = kwargs.get('agentID')

    def update_age(self):
        self.Age += 1

    def update_dist2city(self, new_dist):
        self.Dist2city = new_dist
