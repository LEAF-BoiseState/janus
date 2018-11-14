# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib.pyplot as plt

N = 100  # Dimensions of the landscape
Nt = 500 # Number of time steps
Nplot = 20 # Interval for plotting world

strict_neighbor = False # A flag about whether to include empty space as dissimilar

f_empty = 0.3 # Fraction of space left empty
f_diff  = 0.4 # Fraction of neighborhood diversity above which someone is uncomfortable
f_move  = 0.3 # Fraction of uncomfortable players allowed to move
 
Red_const = 1.0 # Constant for red players
Blue_const = -1.0 # Constant for blue players

N_empty = np.int64(np.floor(f_empty * N ** 2))
N_red   = np.int64(np.floor((N ** 2 - N_empty)/2))
N_blue  = N_red

# Initialize landscape... create a grid of NaNs that is (N x N) 
World = np.nan * np.ones((N,N))

# Assign initial distribution of RED players to landscape
(row_empty, col_empty) = np.where(np.isnan(World))
perm_vec = np.random.permutation(row_empty.size)
World[row_empty[perm_vec[0:N_red]],col_empty[perm_vec[0:N_red]]] = Red_const

# Assign initial distribution of BLUE players to landscape
(row_empty, col_empty) = np.where(np.isnan(World))
perm_vec = np.random.permutation(row_empty.size)
World[row_empty[perm_vec[0:N_blue]],col_empty[perm_vec[0:N_blue]]] = Blue_const

div_red  = np.zeros((N_red,))
div_blue = np.zeros((N_blue,))


for t in np.arange(Nt,dtype=int):

    if (t % Nplot) == 0:
        plt.figure(figsize=(8,8))
        plt.title('World at time t = '+str(t),fontsize=16)
        plt.imshow(World,animated=True)
        plt.show()
 
    
    # Get the locations of red cells, blue cells, and empty cells
    (row_red,col_red) = np.where(World == Red_const)
    (row_blue,col_blue) = np.where(World == Blue_const)
    (row_empty,col_empty) = np.where(np.isnan(World))
        
    # Get the 8-way diversity metric neighborhood measure for RED players
    for i in np.arange(N_red,dtype=int):
        if row_red[i] == 0:
            start_row = 0;
            end_row = row_red[i] + 1
        elif row_red[i] == (N - 1):
            start_row = row_red[i] - 1
            end_row = (N-1)
        else:
            start_row = row_red[i] - 1
            end_row = row_red[i] + 1
            
        if col_red[i] == 0:
            start_col = 0
            end_col = col_red[i] + 1
        elif col_red[i] == (N - 1):
            start_col = col_red[i] - 1
            end_col = (N-1)
        else:
            start_col = col_red[i] - 1
            end_col = col_red[i] + 1
            
        Neighborhood = World[start_row:(end_row + 1),start_col:(end_col + 1)]


        if(strict_neighbor):
            if(np.sum(~np.isnan(Neighborhood))==1): # If surrounded by empty space
                div_red[i] = 1.0
            else:
                div_red[i] = np.sum(Neighborhood == Blue_const) / (np.sum(~np.isnan(Neighborhood)) - 1.0)
        else:
            if(np.sum(~np.isnan(Neighborhood))==1): # If surrounded by empty space
                div_red[i] = 0.0
            else:
                div_red[i] = np.sum(Neighborhood == Blue_const) / np.min([Neighborhood.size,8])
        
    
    # Get the 8-way diversity metric neighborhood measure for BLUE players
    for j in np.arange(N_blue,dtype=int):
        if row_blue[j] == 0:
            start_row = 0;
            end_row = row_blue[j] + 1
        elif row_blue[j] == (N - 1):
            start_row = row_blue[j] - 1
            end_row = (N-1)
        else:
            start_row = row_blue[j] - 1
            end_row = row_blue[j] + 1
            
        if col_blue[j] == 0:
            start_col = 0
            end_col = col_blue[j] + 1
        elif col_blue[j] == (N - 1):
            start_col = col_blue[j] - 1
            end_col = (N-1)
        else:
            start_col = col_blue[j] - 1
            end_col = col_blue[j] + 1
            
        Neighborhood = World[start_row:(end_row + 1),start_col:(end_col + 1)]

        if(strict_neighbor):
            if(np.sum(~np.isnan(Neighborhood))==1): # If surrounded by empty space
                div_blue[j] = 1.0
            else:
                div_blue[j] = np.sum(Neighborhood == Red_const) / (np.sum(~np.isnan(Neighborhood)) - 1.0)
        else:
            if(np.sum(~np.isnan(Neighborhood))==1): # If surrounded by empty space
                div_blue[j] = 0.0
            else:
                div_blue[j] = np.sum(Neighborhood == Red_const) / np.min([Neighborhood.size,8])
    
        
    # Get the locations of those RED players that are uncomfortable    
    uncomfort_red = np.where(div_red > f_diff)

    # Randomly move some fraction of uncomfortable RED players to empty locations
    if uncomfort_red[0].size > 0:
    
        N_uc_red  = uncomfort_red[0].size
        N_move_red  = np.int64(f_move * N_uc_red)
    
        uncomfort_red_row = row_red[uncomfort_red[0]]
        uncomfort_red_col = col_red[uncomfort_red[0]]
    
        perm_vec_red = np.random.permutation(np.int64(N_uc_red))
    
        move_red_row = uncomfort_red_row[perm_vec_red[0:N_move_red]]
        move_red_col = uncomfort_red_col[perm_vec_red[0:N_move_red]]
    
        perm_vec_empty     = np.random.permutation(np.int64(N_empty))
        row_new_empty_red  = row_empty[perm_vec_empty[0:N_move_red]]
        col_new_empty_red  = col_empty[perm_vec_empty[0:N_move_red]]
            
        World[row_new_empty_red,col_new_empty_red] = Red_const
    
        World[move_red_row,move_red_col] = np.nan


    # Get the locations of those RED players that are uncomfortable    
    uncomfort_blue = np.where(div_blue > f_diff)

    # Randomly move some fraction of uncomfortable BLUE players to empty locations
    if uncomfort_blue[0].size > 0:
        N_uc_blue = uncomfort_blue[0].size    
        N_move_blue = np.int64(f_move * N_uc_blue)
            
        uncomfort_blue_row = row_blue[uncomfort_blue[0]]
        uncomfort_blue_col = col_blue[uncomfort_blue[0]]
        
        perm_vec_blue = np.random.permutation(np.int64(N_uc_blue))
            
        move_blue_row = uncomfort_blue_row[perm_vec_blue[0:N_move_blue]]
        move_blue_col = uncomfort_blue_col[perm_vec_blue[0:N_move_blue]]
    
        row_new_empty_blue = row_empty[perm_vec_empty[(N_move_red+1):(N_move_red + N_move_blue+1)]]
        col_new_empty_blue = col_empty[perm_vec_empty[(N_move_red+1):(N_move_red + N_move_blue+1)]]
    
        World[row_new_empty_blue,col_new_empty_blue] = Blue_const
        
        World[move_blue_row,move_blue_col] = np.nan
    

plt.figure(figsize=(8,8))
plt.title('World at time t = '+str(Nt),fontsize=16)
plt.imshow(World,animated=True)
plt.show()
