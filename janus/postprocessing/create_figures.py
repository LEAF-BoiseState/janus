"""
Created on Mon Aug 12 15:35:49 2019

@author: kek25
"""

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import janus.agents.farmer as farmer


def create_animation(crop_id_all, nt):
    """ Create gif of land cover over time

    :param crop_id_all: numpy array of land cover over time
    :param nt:          number of time steps

    :return: Animation of crops over time

    """
    ims = []

    fig = plt.figure(figsize=(12, 12))

    for t in np.arange(nt):
        im = plt.imshow(crop_id_all[t,:,:], interpolation='none')
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)

    ani.save('CropID_vs_Time.gif')


def plot_crop_percent(crop_id_all, CropIDs, nt, nc, scale, results_path, key_file, ag_cats):
    """Stackplot of crops over time

    :param crop_id_all:  numpy array of gridded landcover over time
    :param CropIDs:      numpy array of the crop identification numbers
    :param nt:           number of time steps
    :param nc:           number of crops
    :param scale:        scale of cells within domain
    :param results_path: path to local results folder
    :param key_file:     key file that has conversions from CDL to GCAM or local categories
    :param ag_cats:      categories that are agricultural

    :return:  image saved to results folder of the percentage of each crop over time

    """
    ag_area=np.empty(shape=(nc, nt))
    for t in np.arange(nt):
       cur_crop = crop_id_all[t,:,:]
       for c in np.arange(nc):
           bools=(cur_crop == CropIDs[c])
           ag_area[c,t]=np.sum(bools)
        
    agTot = np.sum(ag_area, axis=0)

    names = []
    percentages = np.zeros((nc, nt))
    data = []
    for c in np.arange(nc):
        name = 'percentages[' + str(c) + ',:]'
        names.append(name)
        for t in np.arange(nt):
            CropIx = CropIDs[c]
            percentages[c, t] = np.sum((crop_id_all[t, :, :] == CropIx)) / agTot[t] * 100.0
        data.append(percentages[c, :])
    
    y = np.vstack(data)
    
    t = np.arange(nt)
    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12))
    
    #pull out any crops planted in the timeseries for legend
    active_crops=np.any(percentages, axis=1)
    ag=np.transpose(np.array(ag_cats))
    ac=np.array(ag[active_crops]).flatten()
    
    ax.stackplot(t,y, labels=key_file['local_GCAM_Name'][ac])
    ax.set_xlim([0, nt - 1])
    ax.set_ylim([0, 100])
    ax.grid()
    ax.legend(loc='lower right')

    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, 'CropPercentages_{}m_{}yr.eps'.format(scale, nt))

    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()

def plot_agent_ages(domain, AgentArray, Ny, Nx, nt, scale, results_path):
    """Histogram of agent ages at end of model run

    :param domain: domain with agent data
    :param AgentArray: numpy array with identifiers of which agent is in each cell
    :param Ny: Number of rows
    :param Nx: Number of columns
    :param nt: Number of time steps
    :param results_path: path to local results folder

    :return: Image saved to results folder of a histogram of farmer ages at the end of the model run

    """

    FarmerAges = []
    for i in np.arange(Ny):

        for j in np.arange(Nx):

            if AgentArray[i, j] == farmer.Farmer.__name__:

                FarmerAges = np.append(FarmerAges, domain[i, j].FarmerAgents[0].Age)

    plt.rcParams.update({'font.size': 16})
    plt.hist(FarmerAges)
    
    output_figure = os.path.join(results_path, 'AgentAges_{}m_{}yr.png'.format(scale, nt))
    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()
