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
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

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
        im = plt.imshow(crop_id_all[t, :, :], interpolation='none')
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
    percentages = np.zeros((nc, nt))
    for c in np.arange(nc):
        for t in np.arange(nt):
            CropIx = CropIDs[c]
            percentages[c, t] = np.sum((crop_id_all[t, :, :] == CropIx)) / agTot[t] * 100.0
    t = np.arange(nt)

    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12))

    # pull any crops planted in the time series for legend
    active_crops = np.any(percentages, axis=1)
    ag = np.transpose(np.array(ag_cats))
    ac = np.array(ag[active_crops]).flatten()

    clrs = ["powder blue", "windows blue", "royal blue", "sand", "grey blue", "greyish", "amber", "light gold",
            "faded green", "washed out green", "pea soup", "rose", "light grey", "dark teal", "jungle green",
            "dusty purple", "black", "bright purple", "green", "crimson", "eggshell","red orange", "burple",
            "battleship grey","black", 'black']
    cc = dict(enumerate(clrs))
    cl = [cc[x] for x in ac]
    col = sns.xkcd_palette(cl)

    ax.stackplot(t, percentages[active_crops, :], baseline='wiggle', labels=key_file['local_GCAM_Name'][ac], colors=col)

    ax.set_xlim([0, nt - 1])
    # ax.set_ylim([0, 90])
    ax.grid()
    ax.legend(loc='upper right')

    ax.set_ylabel('Percent Crop Choice')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, 'CropPercentages_{}m_{}yr.pdf'.format(scale, nt))

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
        out[i] = crpdec.switching_prob_curve(alpha_params[i], beta_params[i], fmin, fmax, n, 1000)  # profit_act[i]

    # TODO: Why is the x scale so large?
    plt.rcParams.update({'font.size': 16})
    # TODO: make these a multi-plot
    ax = plt.axes()
    for i in np.arange(len(out)):
        ax.plot(out[i][0], out[i][1], color=col[i])

    ax.set_ylabel('Probability of switching')
    ax.set_xlabel('Profit')
    # plt.hist(alpha_params)
    # plt.text(250, 4, Counter(col).keys()[0]':'Counter(col).values())
    # plt.set_ylabel('Alpha')
    # plt.set_xlabel('Count')

    output_figure = os.path.join(results_path, 'Switching_curves_{}m_{}yr.png'.format(scale, nt))
    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()


def plot_price_signals(price_file, key, year, nt, results_path, profits_type):
    labs = key['local_GCAM_Name'][key['GCAM_price_id'].notna()]
    ts = np.arange(year, year + nt)

    ax = plt.axes()
    for i in np.arange(len(price_file)):
        ax.plot(ts, price_file[i, :])  # , color=col[i])
    # TODO: add legend in
    # ax.legend(loc='lower right')
    ax.set_ylabel('Crop Price $ per km2')
    ax.set_xlabel('Time [yr]')

    output_figure = os.path.join(results_path, '{}_price_signals.pdf'.format(profits_type))
    plt.savefig(output_figure, dpi=300, facecolor='w', edgecolor='w', bbox_inches='tight')
    plt.close()


def plot_lc(crop_id_all, t, year, results_path, ag_cats, CropIDs, nc, nt, key_file):
    """ Create spatial plot of land cover at a certain time

    :param crop_id_all: numpy array of land cover over time
    :param t:          time step to plot

    :return: Spatial plot of land cover

    """
    percentages = np.zeros((nc, nt))
    print(CropIDs)
    key_file['local_GCAM_id_list']
    for c in np.arange(nc):
        for j in np.arange(nt):
            CropIx = CropIDs[c]
            percentages[c, j] = np.sum((crop_id_all[j, :, :] == CropIx))
    # pull any crops planted in the time series for plotting
    active_crops = np.any(percentages, axis=1)
    active_crops.astype(np.int)
    sub = CropIDs[active_crops]
    print(sub)
    ac = np.array(sub).flatten()
    print(ac)

    #ag = np.transpose(np.array(ag_cats))
    #ac = np.array(ag[active_crops]).flatten()
    xclrs = ["white", "powder blue", "windows blue", "royal blue", "sand", "grey blue", "greyish", "amber", "light gold",
            "faded green", "washed out green", "pea soup", "rose", "light grey", "dark teal", "jungle green",
            "dusty purple", "black", "bright purple", "jungle green", "crimson", "egg shell","red orange"]
    clrs = ["white", "powder blue", "windows blue", "royal blue", "sand", "grey blue", "greyish", "amber", "light gold",
            "faded green", "washed out green", "pea soup", "rose", "light grey", "dark teal", "jungle green",
            "dusty purple", "black", "bright purple", "jungle green", "crimson", "egg shell","red orange"]
    cc = dict(enumerate(clrs))
    print(cc)
    cl = [cc[x] for x in ac]
    print(cl)

    legend_labels = {"Corn":"xkcd:powder blue", "Wheat":"xkcd:windows blue", "Dry Beans": "xkcd:royal blue", "Root/Tuber": "xkcd:sand", "Oil Crop":"xkcd:grey blue", "Sugar Crop": "xkcd:greyish", "Other Grain":"xkcd:amber", "Onions":"xkcd:light gold", "Fodder Grass": "xkcd:faded green","FodderHerb": "xkcd:washed out green", "Peas":"xkcd:pea soup", "Misc crop": "xkcd:rose", "Other":"xkcd:light grey", "Sod":"xkcd:dark teal", "Pasture":"xkcd:jungle green", "Hops":"xkcd:dusty purple", "Stone/Pomme Fruit":"xkcd:bright purple", "Urban":"xkcd:black","Grapes":"xkcd:crimson", "Mint":"xkcd:red orange"}

    xcol = sns.xkcd_palette(cl)
    col = ListedColormap(xcol.as_hex())
    crops = crop_id_all[t, :, :]
    crops = crops.astype('float')
    crops[crops == 0] = 'nan'

    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.imshow(crops, interpolation='none', cmap=col)
    patches = [Patch(color=color, label=label)
               for label, color in legend_labels.items()]

    ax.legend(handles=patches,
              bbox_to_anchor=(1.35, 1),
              facecolor="white")
    output_figure = os.path.join(results_path, 'landcover_{}.pdf'.format(year + t))
    plt.savefig(output_figure, dpi=300)
    plt.close()
