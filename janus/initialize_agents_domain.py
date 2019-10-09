"""
Created on Mon Aug 12 11:15:12 2019

@author: kek25
"""
import numpy as np

import janus.agents.farmer as farmer
import janus.agents.d_cell as cell
import janus.agents.urban as urban
import janus.preprocessing.getNASSAgentData as getNASS


def initialize_domain(Ny, Nx):
    """

    :param Ny:
    :param Nx:

    :return:

    """
    domain = np.empty((Ny, Nx), dtype=object)

    for i in np.arange(Ny):

        for j in np.arange(Nx):

            domain[i][j] = cell.Dcell()

    return domain


def place_agents(Ny, Nx, lc, key_file, cat_option):
    """

    :param Ny:
    :param Nx:
    :param lc:
    :param key_file:
    :param cat_option:

    :return:

    """
    # assert that cat_option has to be a header in the csv doc
    AgentArray = np.empty((Ny, Nx), dtype='U10')

    if cat_option == 'SRB':

        agent_Cat = key_file['SRB_cat'][0:28]
        code = key_file['SRB_GCAM_id_list'][0:28]

    elif cat_option == 'GCAM':

        agent_Cat = key_file['GCAM_cat'][0:24]
        code = key_file['GCAM_id_list'][0:24]

    ag = np.array(code[agent_Cat == 'ag']).astype(int)
    urb = np.array(code[agent_Cat == 'urb']).astype(int)
    water = np.array(code[agent_Cat == 'water']).astype(int)
    empty = np.array(code[agent_Cat == 'nat']).astype(int)

    # this works, would be better without the for loops
    for i in ag:
        AgentArray[lc[0] == i] = farmer.Farmer.__name__

    for i in water:
        AgentArray[lc[0] == i] = 'water'

    for i in urb:
        AgentArray[lc[0] == i] = urban.Urban.__name__

    for i in empty:
        AgentArray[lc[0] == i] = 'empty'

    return AgentArray


def agents(AgentArray, domain, dist2city, TenureCDF, AgeCDF, switch, Ny, Nx, lc, p):
    """Place agent structures onto landscape and define attributes.

    :param AgentArray:
    :param domain:
    :param dist2city:
    :param TenureCDF:
    :param AgeCDF:
    :param switch:
    :param Ny:
    :param Nx:
    :param lc:
    :param p:

    :return:

    """
    for i in np.arange(Ny):

        for j in np.arange(Nx):

            if AgentArray[i][j] == farmer.Farmer.__name__:

                AgentData = getNASS.FarmerData(TenureCDF, AgeCDF, switch, p, dist2city[i][j])
                NewAgent = farmer.Farmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"],
                                          Dist2city=AgentData["Dist2city"], nFields=AgentData['nFields'],
                                          alpha=AgentData['Alpha'],
                                          beta=AgentData['Beta'])  # this is passing actual agent data
                domain[i][j].add_agent(NewAgent)

            if AgentArray[i][j] == urban.Urban.__name__:

                AgentData = getNASS.UrbanData(lc[0][i][j])
                NewAgent = urban.Urban(density=AgentData["Density"])
                domain[i][j].add_agent(NewAgent)

    return domain


def profits(profit_signals, Nt, Ny, Nx, CropID_all, CropIDs):
    """Initialize np array of profits

    :param profit_signals: data frame of profit signals created from generate synthetic prices, or user supplied
    :param Nt:
    :param Ny:
    :param Nx:
    :param CropID_all: Nt x Nx x Ny np array of current land cover
    :param CropIDs: Num_crop x 1 np array of crop ids

    :return: np array of initial profits based on price signals

    """

    profits_actual = np.zeros((Nt, Ny, Nx))

    for i in np.arange(Ny):

        for j in np.arange(Nx):

            CropInd = CropID_all[0, i, j]
            CropIx = np.where(CropIDs == CropInd)

            if CropInd in (CropIDs):
                profits_actual[0, i, j] = profit_signals[CropIx[0][0], 0]

            else:
                profits_actual[0, i, j] = 0

    return profits_actual
