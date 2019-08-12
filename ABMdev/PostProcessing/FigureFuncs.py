#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 15:35:49 2019

@author: kek25
"""
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def CreateAnimation(CropID_all, Nt):
    ims = []

    fig = plt.figure(figsize=(12,12))
    for t in np.arange(Nt):
        im = plt.imshow(CropID_all[t,:,:], interpolation='none')
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)

    ani.save('CropID_vs_Time.gif')