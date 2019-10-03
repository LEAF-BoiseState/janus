# Author: Jonathan Carvajal
# Date: 8/13/2019
# FileName: aFarmer.py
# Purpose: Holds defination of farmer


class aFarmer:
    
    def __init__(self,**kwargs):

        self.Age = kwargs.get('Age')
        self.Dist2city = kwargs.get('Dist2city')
        
        self.LandStatus = kwargs.get('LandStatus')
        self.LandStatus = self.LandStatus
        
        self.nFields = kwargs.get('nFields')
        self.nFields = self.nFields
        
        self.alpha = kwargs.get('alpha') # write asserts that require the value to be between 0/1 ?
        self.beta = kwargs.get('beta')

    def UpdateAge(self):
        self.Age += 1

    def UpdateDist2city(self, newDist):
        self.Dist2city = newDist
