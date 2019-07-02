#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 13:38:25 2019

@author: Vicken Hillis

Urbanization model incorporating a spatial prisoner's dilemma and conformist transmission of land ethic
"""

import numpy as np
import random
import pandas as pd

x = np.arange(1, 50)
y = np.arange(1, 50)

numstep = 50
numcell = 2500

import itertools
def expandgrid(*itrs):
   product = list(itertools.product(*itrs))
   return pd.DataFrame.from_records(product, columns=['x','y'])

product = list(itertools.product(x,y))
pop = expandgrid(x,y)
pop = np.meshgrid(x,y) # x is 0 and y is 1

adj_mat = np.zeros((numcell, numcell))


#create base network connections between individuals

#have agents move at random 
for i in np.arange(numstep):
    for j in np.arange(numcell):
        z = random.randint(1,4)
        
        if z == 1:
            if : 
        elif :
            
#create adjacency matrix by finding where agents overlap

# here is a new comment, yay!