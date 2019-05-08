#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 12:50:01 2019

@author: lejoflores
"""

import numpy as np
import sys
import traceback

class aFarmer:
    
    def __init__(self, Age, nFields, AreaFields, LandStatus):
        
        self.Age = Age          # Initial age of the farmer in years
        
        if(type(nFields)!=int) & (nFields.is_integer()==False):
            sys.exit("nFields must be passed as a whole number float or integer")
        else:
            self.nFields = nFields  # Number of fields cultivated on farm

        if(AreaFields.size!=self.nFields):
            sys.exit("Size of AreaFields = "+AreaFields.size+" does not match nFields = "+self.nFields)
                
        self.AreaFields = np.nan*np.ones(AreaFields.shape)
        for i in np.arange(self.nFields):
            self.AreaFields[i] = AreaFields[i]
            
        try:
            assert(LandStatus==0 or LandStatus==1 or LandStatus==2)
            self.LandStatus = LandStatus
  
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb) # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
        
            print("Invalid value of LandStatus passed to Fermer constructor".format(line, text))
            exit(1)
            


# Stub to make fields more complex in the future. Unused now
class __Field:
    
    def __init__(self, Area, AvgElev, AvgSlope, AvgAspect, SoilClass):
        
        self.Area = Area
        self.AvgElev = AvgElev
        
        try:
            assert(AvgSlope > 0.0)
            self.AvgSlope = AvgSlope
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb) # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
        
            print("Invalid value of AvgSlope passed to __Field constructor".format(line, text))
            exit(1)
        
        try:
            assert(AvgAspect >= 0.0 and AvgAspect < 360.0)
            self.AvgAspect = AvgAspect
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb) # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
        
            print("Invalid value of AvgAspect passed to __Field constructor".format(line, text))
            exit(1)
            

        self.SoilClass = SoilClass
        