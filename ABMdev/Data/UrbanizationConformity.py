#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 13:38:25 2019
@author: Vicken Hillis
Urbanization model incorporating a spatial prisoner's dilemma and conformist transmission of land ethic
"""

import numpy as np
import random

##### create a network of farmers
##### farmers start in a two-dimensional matrix of size dim
##### farmers take a random walk in cardinal dimensionsw
##### any farmers that end a turn on the same cell become linked

#number of cells in each dimension in the landscape
dim = 50

# number of iterations in the random walk
num_steps = 50

# number of agents in the network
num_agents = dim^2

# create a matrix of x,y locations for each individual
pop = np.array([(x, y) for x in range(dim) for y in range(dim)])

# create a network of zeros representing the social network
adj_mat = np.zeros((2500,2500), dtype=int)

# number of iterations that the random walk will last
for i in range(numstep):
    
    # loop through each of the nodes in the network
    for j in range(numcell):
        
        # pick a random number between 1 and 4 representing the cardinal direction the agent will move
        z = random.randint(1,4)
        
        # for each of the four cardinal directions, reassign the agent's location appropriately
        if z == 1:
            
            pop[j,0] = pop[j,0] - 1
            
            # if the agent has left the dim X dim grid, reassign them to the other side            
            if pop[j,0] < 0: pop[j,0] = dim - 1
                
        elif z == 2:
            
            pop[j,1] = pop[j,1] - 1
            
            if pop[j,1] < 0: pop[j,1] = dim - 1
            
        elif z == 3:
            
            pop[j,0] = pop[j,0] + 1
            
            if pop[j,0] == dim: pop[j,0] = 0
            
        elif z == 4:
            
            pop[j,1] = pop[j,1] + 1
            
            if pop[j,1] == dim: pop[j,1] = 0
    
    # after each of the dim^2 agents has moved, find all the agents in the same location
    # for each row in pop array, find all other matching rows
    for k in range(numcell):
                
        zzz = np.flatnonzero((pop == pop[k]).all(axis=1))

        for kk in zzz:
            
            adj_mat[ k , kk] = 1
            adj_mat[ kk , k] = 1

        
        
            
# R code below here
# do this for the number of iterations (50)
# do this for each cell

  
  for (ii in 1:numcell){
    adj_mat[ which( match(r, r[ii]) == 1)[1], which( match(r, r[ii]) == 1)[2] ] <- 1
    adj_mat[ which( match(r, r[ii]) == 1)[2], which( match(r, r[ii]) == 1)[1] ] <- 1
  }
  
}
