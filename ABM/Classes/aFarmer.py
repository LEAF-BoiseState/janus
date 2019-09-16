# Author: Jonathan Carvajal
# Date: 8/13/2019
# FileName: aFarmer.py
# Purpose: Holds defination of farmer

#!/usr/bin/env python3

import numpy as np

class aFarmer:
    
    def __init__(self,**kwargs):
        self._Validate(kwargs)
        self.Age = kwargs.get('Age')
        self.nFields = kwargs.get('nFields')
        self.AreaFields = kwargs.get('AreaFields')
        self.LandStatus = kwargs.get('LandStatus')
        self.Dist2city = kwargs.get('Dist2city')
        self.AreaFields = kwargs.get('AreaFields')

        self.AreaFields = np.nan*np.ones(self.AreaFields.shape)
        for i in np.arange(self.nFields):
            self.AreaFields[i] = self.AreaFields[i]

        self.LandStatus = self.LandStatus

    def UpdateAge(self):
        self.Age += 1

    def UpdateDist2city(self, newDist):
        self.Dist2city = newDist

############### Private Functions ###############
    @staticmethod
    def _Validate(self, **kwargs):
        if type(self.nFields)!=int: raise Exception("nFields is not valid: Invalid Type")
        if self.AreaFields.size != self.nFields: raise Exception("nFields is not valid: Invalid Size")
        if self.LandStatus == 0 or self.LandStatus == 1 or self.LandStatus == 2: raise Exception("LandStatus is not valid: Invalid Status")