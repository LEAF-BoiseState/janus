"""
Created on Mon Aug 12 15:35:49 2019

@author: Kendra Kaiser
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns

import janus.agents.farmer as farmer
import janus.crop_functions.crop_decider as crpdec
from collections import Counter

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
    """Stack plot of crops over time

    :param crop_id_all:  numpy array of gridded land cover over time
    :param CropIDs:      numpy array of the crop identification numbers
    :param nt:           number of time steps
    :param nc:           number of crops
    :param scale:        scale of cells within domain
    :param results_path: path to local results folder
    :param key_file:     key file that has conversions from CDL to GCAM or local categories
    :param ag_cats:      categories that are agricultural

    :return:  image saved to results folder of the percentage of each crop over time

    """
    ag_area = np.empty(shape=(nc, nt))
    for t in np.arange(nt):
       cur_crop = crop_id_all[t, :, :]
       for c in np.arange(nc):
           bools = (cur_crop == CropIDs[c])
           ag_area[c, t] = np.sum(bools)
        
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
    #print(CropIDs)
    #print(percentages[:, -1])
    y = np.vstack(data)
    t = np.arange(nt)

    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12))
    
    # pull any crops planted in the time series for legend
    active_crops = np.any(percentages, axis=1)
    ag = np.transpose(np.array(ag_cats))
    ac = np.array(ag[active_crops]).flatten()

    print(ac)
    print(key_file['local_GCAM_Name'][ac])

    clrs = ["powder blue", "windows blue", "royal blue", "amber", "ochre", "greyish", "faded green", "dark teal", "jungle green", "dusty purple", "bright purple",  "crimson", "red orange", "coral", ]
    col = sns.xkcd_palette(clrs)
    #col = sns.color_palette("Paired", len(ac))
    ax.stackplot(t, y, colors=col)

    #palette = plt.get_cmap('Set1', len(ac))
    #num=0
    #for c in np.arange(len(y)):
     #  ax.plot(t, y[c, :], linewidth=2, color=palette(num))

    ax.set_xlim([0, nt - 1])
    ax.set_ylim([0, 90])
    ax.grid()
    ax.legend(loc='upper right', labels=key_file['local_GCAM_Name'][ac])

    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, 'CropPercentages_{}m_{}yr.png'.format(scale, nt))

    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()


def plot_agent_ages(domain, AgentArray, Ny, Nx, nt, scale, results_path):
    """Histogram of agent ages at end of model run

    :param domain:       Domain with agent data
    :param AgentArray:   Numpy array with identifiers of which agent is in each cell
    :param Ny:           Number of rows
    :param Nx:           Number of columns
    :param nt:           Number of time steps
    :param scale:        Scale of cells within domain
    :param results_path: Path to local results folder

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


def plot_switching_curves(domain, AgentArray, fmin, fmax, Ny, Nx, nt, n, scale, results_path, profits, switch_params):
    """Histogram of agent ages at end of model run

    :param domain:       Domain with agent data
    :param AgentArray:   Numpy array with identifiers of which agent is in each cell
    :param fmin:         The fraction of current profit at which the CDF of the beta distribution is zero
    :param fmax:         The fraction of current profit at which the CDF of the beta distribution is one
    :param Ny:           Number of rows
    :param Nx:           Number of columns
    :param nt:           Number of time steps
    :param n:            The number of points to generate in the CDF
    :param scale:        Scale of cells within domain
    :param profits:      Numpy array of profits from the last time step
    :param results_path: path to local results folder

    :return: Image saved to results folder of a histogram of farmer ages at the end of the model run

    """

    alpha_params = []
    beta_params = []
    profit_act = []

    for i in np.arange(Ny):
        for j in np.arange(Nx):
            if AgentArray[i, j] == farmer.Farmer.__name__:
                alpha_params = np.append(alpha_params, domain[i, j].FarmerAgents[0].alpha)
                beta_params = np.append(beta_params, domain[i, j].FarmerAgents[0].beta)
                profit_act = np.append(profit_act, profits[i, j])

    col = [0] * len(alpha_params)
    for i in np.arange(len(alpha_params)):
        if alpha_params[i] >= switch_params[0][0]:
            col[i] = 'k'
        else:
            col[i] = 'b'

    out = [0] * len(alpha_params)
    for i in np.arange(len(alpha_params)):
        out[i] = crpdec.switching_prob_curve(alpha_params[i], beta_params[i], fmin, fmax, n, 1000) #profit_act[i]
    print(len(col))
    print(Counter(col).keys())
    print(Counter(col).values())
# TODO: Why is the x scale so large?
    plt.rcParams.update({'font.size': 16})
    # TODO: make these a multi-plot
    ax = plt.axes()
    for i in np.arange(len(out)):
        ax.plot(out[i][0], out[i][1], color=col[i])

    ax.set_ylabel('Probability of switching')
    ax.set_xlabel('Profit')
    #plt.hist(alpha_params)
    #plt.text(250, 4, Counter(col).keys()[0]':'Counter(col).values())
    #plt.set_ylabel('Alpha')
    #plt.set_xlabel('Count')

    output_figure = os.path.join(results_path, 'Switching_curves_{}m_{}yr.png'.format(scale, nt))
    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()

def plot_price_signals(price_file, key, year, nt, results_path, profits_type):

    labs = key['local_GCAM_Name'][key['GCAM_price_id'].notna()]
    ts = np.arange(year, year+nt)

    ax = plt.axes()
    for i in np.arange(len(price_file)):
        ax.plot(ts, price_file[i, :]) #  , color=col[i])
    # TODO: add legend in
    # ax.legend(loc='lower right')
    ax.set_ylabel('Crop Price $ per km2')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, '{}_price_signals.png'.format(profits_type))
    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()

def plot_lc(crop_id_all, t, year, results_path):
    """ Create spatial plot of land cover at a certain time

    :param crop_id_all: numpy array of land cover over time
    :param t:          time step to plot

    :return: Spatial plot of land cover

    """

    plt.figure(figsize=(12, 12))
    plt.imshow(crop_id_all[t, :, :], interpolation='none')

    output_figure = os.path.join(results_path, 'landcover_{}.png'.format(year+t))
    plt.savefig(output_figure, dpi=300)
    plt.close()
