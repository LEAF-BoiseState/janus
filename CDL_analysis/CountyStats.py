#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 08:46:08 2019

@author: kendrakaiser

Initial CDL analysis across scales

This includes shannons diversity across each county and plots things over time.
"""

import glob
#import gdal
import rasterio as rio
#from rasterio.plot import show
from rasterio.plot import show_hist
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
#import matplotlib
from matplotlib import cm
from matplotlib.patches import Patch
#from matplotlib.colors import ListedColormap
import matplotlib.colors as colors

os.chdir('/Users/kek25/Documents/GitRepos/IM3-BoiseState/CDL_analysis')

crop_key = pd.read_csv("GCAM_SRP_names.csv", sep=',')
key=np.asarray(crop_key['crop'])
crop_key = crop_key.values

#ReadDir = '/Users/kendrakaiser/Documents/Data/GCAM_UTM/Jerome_2010/' #need a way to index into multiple folders...
ReadDir = '/Users/kek25/Dropbox/BSU/IM3/Data/GCAM_UTM/Jerome/'
files = glob.glob(ReadDir +'*.tiff')
files.sort()

years=['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
yrs=[0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6,7,7,7]
scale=[0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2]
#create a dictionary to hold counts of each cover type over all years for each resoultion
counts={}
for y in np.arange(8):
    counts[years[y]]={}   
for y in np.arange(8):
    for j in np.arange(28):
        counts[years[y]][crop_key[j,0]]=[0,0,0]
    
#open each file and count number of pixels of each landcover 
for i in np.arange(24):

    with rio.open(files[i]) as src:
        r =src.read(1)
        cdl=r[r>0] #flattens the data
  
    for j in np.arange(28): 
       counts[years[yrs[i]]][j+1][scale[i]]=np.count_nonzero(cdl == j+1) 


#calculate Shannon diversity index for each year at each scale
import skbio.diversity as sci

l=np.zeros((28,3))
sh=np.zeros((8,3))

for y in np.arange(8):
    x= counts[years[y]]
    for s in np.arange(3):
        temp = []
        dictlist = []
        for key, value in x.items():
            temp = value[s]
            dictlist.append(temp)
        
        l[:,s]=np.asarray(dictlist)

        sh[y,s]=sci.alpha.shannon(l[:,s])

plt.plot(sh)
plt.title('Jerome County Crop Diversity')
plt.ylabel('Shannons Diversity Index')
plt.xlabel('Year')
plt.gca().legend(('1km','3km', '30m'))
plt.xticks(np.arange(8),labels=years)
plt.show

###30 meter resolution
m30= np.zeros((28,8))
for y in np.arange(8):
    x= counts[years[y]]
    temp = []
    dictlist = []
    for key, value in x.items():
        temp = value[2]
        dictlist.append(temp)
        
    l=np.asarray(dictlist)
    m30[:,y]=l
    
np.savetxt('Jerome30m', m30, delimiter=",")

pix=sum(m30[:,0])
perc=m30/pix

m30t=np.ndarray.transpose(perc)

plt.plot(m30t)
plt.title('Jerome County land cover (30m)')
plt.ylabel('Percent')
plt.xlabel('Year')
plt.xticks(np.arange(8),labels=years)
plt.ylim((0,0.08))

### 3km res - basically captures all large crops, small crops like mint/hops are gone
m3k= np.zeros((28,8))
for y in np.arange(8):
    x= counts[years[y]]
    temp = []
    dictlist = []
    for key, value in x.items():
        temp = value[1]
        dictlist.append(temp)
        
    l=np.asarray(dictlist)
    m3k[:,y]=l
    
np.savetxt('Jerome3km.csv', m3k, delimiter=",")

pix=sum(m3k[:,0])
perc=m3k/pix

m3kt=np.ndarray.transpose(perc)

plt.plot(m3kt)
plt.title('Jerome County land cover (3km)')
plt.ylabel('Percent')
plt.xlabel('Year')
plt.xticks(np.arange(8),labels=years)
plt.ylim((0,0.04))













### TRYING TO MAP COLORS TO EACH LANDCOVER TYPE
viridis = cm.get_cmap('viridis', 27)

cmap=colors.LinearSegmentedColormap.from_list('viridis', viridis.colors, N=27)

legend_labels={}
legend_labels = {viridis(0) : crop_key[1,1], viridis(1) : crop_key[2,1], viridis(2) : crop_key[3,1], viridis(3) : crop_key[4,1], viridis(4) : crop_key[5,1], viridis(5) : crop_key[6,1], viridis(6) : crop_key[7,1], viridis(7) : crop_key[8,1],
                 viridis(8) : crop_key[9,1], viridis(9) : crop_key[10,1], viridis(10) : crop_key[11,1], viridis(11) : crop_key[12,1], viridis(12) : crop_key[13,1], viridis(13) : crop_key[14,1], viridis(14) : crop_key[15,1],
                 viridis(15) : crop_key[16,1], viridis(16) : crop_key[17,1], viridis(17) : crop_key[18,1], viridis(18) : crop_key[19,1], viridis(19) : crop_key[20,1], viridis(20) : crop_key[21,1], viridis(21) : crop_key[22,1],
                 viridis(22) : crop_key[23,1], viridis(23) : crop_key[24,1], viridis(24) : crop_key[25,1], viridis(25) : crop_key[26,1], viridis(26) : crop_key[27,1]}
 

#### TRYING TO PLOT ####  
for i in np.arange(3):

    with rio.open(files[i]) as src:
        r =src.read(1)
        r[r==0]=np.nan
        
    fig, (leg, ax, ax2) = plt.subplots(1,3, figsize=(15,5))
    ax.imshow(r, cmap = cmap)
    ax.set_axis_off()
    
    ax2.hist(cdl, density=True)
    ax2.set(xlabel = 'Crop', 
            ylabel = 'Frequency')
    fig.suptitle("Distribution of crop categories in Jerome County 2010")
    
   

    patches = [Patch(color=color, label=label) for color, label in legend_labels.items()]
    leg.legend(handles=patches, 
              bbox_to_anchor=(1.35,1), 
              facecolor="white")
    leg.set_axis_off()
    
show_hist(cdl, lw=0.0)


    
height=[5, 4, 4, 1, 12,5, 4, 4, 1, 12,5, 4, 4, 1, 12,5, 4, 4, 1, 12,5, 4, 4, 1, 12,5,6, 8]
count=np.arange(28)
plt.bar(count, height, color=cmap)


s = pd.Series(
    height,
    index = crop_key[:,1]
)
s.plot( 
    kind='bar', 
    color=cmap,
)