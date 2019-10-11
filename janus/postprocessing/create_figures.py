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
    """ Create gif of landcover over time

    :param crop_id_all: numpy array of landcover over time
    :param nt:          number of timesteps

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
    """Stackplot of crops over time; automate stackplot naming conventions

    :param crop_id_all:  numpy array of gridded landcover over time
    :param CropIDs:      numpy array of the crop identification numbers
    :param nt:           number of timesteps
    :param nc:           number of crops
    :param scale:        scale of cells within domain
    :param results_path: path to loacl results folder
    :param key_file:     key file that has conversions from CDL to GCAM or local categories
    :param ag_cats:      categories that are agricultural

    :return:  image saved to results folder of the percentag of each crop over time

    """
    # TODO:  This value need to be de-hard-coded
    ag_area=np.empty(shape=(nc, nt))
    for t in np.arange(nt):
       cur_crop = crop_id_all[t,:,:]
       for c in np.arange(nc):
           bools=(cur_crop == CropIDs[c])
           #unq, counts=np.unique(cur_crop, return_counts=True)
           ag_area[c,t]=np.sum(bools)
        
    agTot = np.sum(ag_area, axis=0)

    names = [key_file['local_GCAM_Name'][ag_cats[0]]]
    percentages = np.zeros((nc, nt))
    for c in np.arange(nc):
        name = 'percentages[' + str(c) + ',:]'
        names.append(name)
        for t in np.arange(nt):
            CropIx = CropIDs[c]
            percentages[c, t] = np.sum((crop_id_all[t, :, :] == CropIx)) / agTot[t] * 100.0

    t = np.arange(nt)
    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12))

    # set colors to come color scheme w nc colors
    # figure out how to automate the number of percentages in the stackplot
    ax.stackplot(t, percentages[0, :], percentages[1, :], percentages[2, :], percentages[3, :],
                 labels=key_file['local_GCAM_Name'][ag_cats[0]])
    ax.set_xlim([0, nt - 1])
    ax.set_ylim([0, 100])
    ax.grid()
    ax.legend(loc='lower left')

    ax.set_ylabel('Percent Crop Choice')
    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, 'CropPercentages_{}m_{}yr.png'.format(scale, nt))

    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')


def plot_agent_ages(domain, AgentArray, Ny, Nx, nt, nc, scale, results_path):
    """

    :param domain:
    :param AgentArray:
    :param Ny:
    :param Nx:

    :return:

    """

    FarmerAges = []
    for i in np.arange(Ny):

        for j in np.arange(Nx):

            if AgentArray[i, j] == farmer.Farmer.__name__:

                FarmerAges = np.append(FarmerAges, domain[i, j].FarmerAgents[0].Age)


    plt.hist(FarmerAges)
   
    output_figure = os.path.join(results_path, 'AgentAges_{}m_{}yr.png'.format(scale, nt))

    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
