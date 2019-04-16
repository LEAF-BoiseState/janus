#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 14:22:33 2018

@author: kek25
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


#os.chdir("/Users/kek25/Dropbox/BSU/IM3")

gcam_base = pd.read_csv('SRB_2010_Area_Price_Yield.csv', sep=',')

SRB_crops=gcam_base[gcam_base['Value'].notna()]
SRB_crops= SRB_crops.sort_values(by='Value', ascending=False)

ax=SRB_crops['Value'].plot(kind='barh')
plt.gca().invert_yaxis()
<<<<<<< HEAD
ax.set_yticklabels(SRB_crops.iloc[:,1])
ax.set_ylabel("Snake River Crops", labelpad=20, weight='bold', size=12)
ax.set_xlabel("2010 Crop Value ($)", labelpad=20, weight='bold', size=12)
=======
ax.set_yticklabels(SRB_crops['SRB_GCAM'].values)
ax.set_ylabel("Snake River GCAM crops", labelpad=20, weight='bold', size=12)
>>>>>>> 58cc171335d31a370547e2b21c0eebd61034e702
plt.show()
