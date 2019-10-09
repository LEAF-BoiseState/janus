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
    """

    :param crop_id_all:
    :param nt:

    :return:

    """
    ims = []

    fig = plt.figure(figsize=(12, 12))

    for t in np.arange(nt):
        im = plt.imshow(crop_id_all[t,:,:], interpolation='none')
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)

    ani.save('CropID_vs_Time.gif')


def plot_crop_percent(CropID_all, CropIDs, Nt, Nc, scale, ResultsPath, key_file, ag_cats):
    """Stackplot of crops over time; automate stackplot naming conventions

    :param CropID_all:
    :param CropIDs:
    :param Nt:
    :param Nc:
    :param scale:
    :param ResultsPath:
    :param key_file:
    :param ag_cats:

    :return:

    """
    # TODO:  This value need to be de-hard-coded
    agTot = 59  # need to automate what the total area in crops is - this will be a unit test when urban isnt changing

    names = []
    percentages = np.zeros((Nc, Nt))
    for c in np.arange(Nc):
        name = 'percentages[' + str(c) + ',:]'
        names.append(name)
        for t in np.arange(Nt):
            CropIx = CropIDs[c]
            percentages[c, t] = np.sum((CropID_all[t, :, :] == CropIx)) / agTot * 100.0

    t = np.arange(Nt)
    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12))

    # set colors to come color scheme w Nc colors
    # figure out how to automate the number of percentages in the stackplot
    ax.stackplot(t, percentages[0, :], percentages[1, :], percentages[2, :], percentages[3, :],
                 labels=key_file['GCAM_SRB_Name'][ag_cats[0]])
    ax.set_xlim([0, Nt - 1])
    ax.set_ylim([0, 100])
    ax.grid()
    ax.legend(loc='lower left')

    ax.set_ylabel('Percent Crop Choice')
    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(ResultsPath, 'CropPercentages_{}m_{}yr.png'.format(scale, Nt))

    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')


def plot_agent_ages(domain, AgentArray, Ny, Nx):

    FarmerAges = []
    for i in np.arange(Ny):

        for j in np.arange(Nx):

            if AgentArray[i, j] == farmer.Farmer.__name__:

                FarmerAges = np.append(FarmerAges, domain[i, j].FarmerAgents[0].Age)

    # TODO:  does this need to be saved as an output?
    plt.hist(FarmerAges)
