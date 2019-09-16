#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 09:13:41 2019

@author: kek25
need to add assertions
urban agents are initially one agent per cell with a density attribute
their only action is to buy ag land, that is a decision function that is based on the prisoners dilema... where does that go in the code?
"""

import sys
import traceback

class aUrban:
    
    def __init__(self, density):
        
        try:
            assert(density==0 or density==1 or density==2)
            self.density = density
            
        except AssertionError: #how does this work?
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb) # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
        
            print("Invalid Density value passed to Urban constructor".format(line, text))
            exit(1)
            
            