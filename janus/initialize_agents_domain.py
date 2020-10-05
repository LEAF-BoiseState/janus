"""
Created on Mon Aug 12 11:15:12 2019

@author: kek25
"""
import numpy as np

import janus.agents.farmer as farmer
import janus.agents.d_cell as cell
import janus.agents.urban as urban
import janus.preprocessing.get_nass_agent_data as getNASS


def initialize_domain(Ny, Nx):
    """

    :param Ny: Number of columns in domain
    :param Nx: Number of rows in domain

    :return: empty numpy array filled with class Dcell at each pixel

    """
    domain = np.empty((Ny, Nx), dtype=object)

    for i in np.arange(Ny):

        for j in np.arange(Nx):

            domain[i][j] = cell.Dcell()

    return domain


def place_agents(Ny, Nx, lc, key_file, cat_option):
    """ Place agents on the landscape based on landcover and associated categorization

    :param Ny: Number of columns in domain
    :param Nx: Number of rows in domain
    :param lc: Initial landcover numpy array
    :param key_file: csv file with categorization from CDL categories to GCAM or user defined categories, see README file.
    :param cat_option:  Set whether using 'GCAM' or 'local'categorization. If the local caracterization has been changed to
    have more or less categories, the number of rows to use in line 52/53 will need to be edited

    :return: numpy array of strings with each agent type

    """
    AgentArray = np.empty((Ny, Nx), dtype='U10')

    if cat_option == 'local':

        agent_Cat = key_file['local_cat'][0:28]
        code = key_file['local_GCAM_id_list'][0:28]

    elif cat_option == 'GCAM':

        agent_Cat = key_file['GCAM_cat'][0:24]
        code = key_file['GCAM_id_list'][0:24]

    ag = np.array(code[agent_Cat == 'ag']).astype(int)
    urb = np.array(code[agent_Cat == 'urb']).astype(int)
    water = np.array(code[agent_Cat == 'water']).astype(int)
    empty = np.array(code[agent_Cat == 'nat']).astype(int)

    # this works, would be better without the for loops
    for i in ag:
        AgentArray[lc == i] = farmer.Farmer.__name__

    for i in water:
        AgentArray[lc == i] = 'water'

    for i in urb:
        AgentArray[lc == i] = urban.Urban.__name__

    for i in empty:
        AgentArray[lc == i] = 'empty'

    return AgentArray


def agents(AgentArray, domain, dist2city, TenureCDF, AgeCDF, switch, Ny, Nx, lc, p, attr):
    """Place agent structures onto landscape and define attributes.

    :param AgentArray: Numpy array of strings of location of each agent type
    :param domain:     Initial domain
    :param dist2city:  Numpy array of distance to city
    :param TenureCDF:  CDF of tenure type in the domain
    :param AgeCDF:     CDF of ages in the domain
    :param switch:     List of lists of parameter sets to describe agent switching behavior
    :param Ny:         Number of columns in domain
    :param Nx:         Number of rows in domain
    :param lc:         Initial land cover numpy array
    :param p:          Percentage of switching averse farming agents

    :return:           Domain with agents in each dCell

    """


    farmer_agent_list = []
    for i in np.arange(Ny):

        for j in np.arange(Nx):

            if AgentArray[i][j] == farmer.Farmer.__name__:
                
                AgentData = getNASS.farmer_data(TenureCDF, AgeCDF, switch, dist2city[i][j], p, attr)
                NewAgent = farmer.Farmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"],
                                          LocationID =(i, j),
                                          Dist2city=AgentData["Dist2city"], nFields=AgentData['nFields'],
                                          alpha=AgentData['Alpha'],
                                          beta=AgentData['Beta'],
                                          agentID=(i, j))
                domain[i][j].add_agent(NewAgent)
                # TODO this might not be referencing agentID properly
                farmer_agent_list.append(farmer.Farmer.agentID)

            if AgentArray[i][j] == urban.Urban.__name__:

                AgentData = getNASS.urban_data(lc[0][i][j])
                NewAgent = urban.Urban(density=AgentData["Density"])
                domain[i][j].add_agent(NewAgent)

    return domain, farmer_agent_list


def init_profits(profit_signals, Nt, Ny, Nx, CropID_all, CropIDs):
    """Initialize np array of profits

    :param profit_signals:  Profit signals created from generate synthetic prices, or user supplied
    :type profit_signals:   Numpy  Array
    :param nt:              Number of time steps
    :type nt:               Int
    :param ny:              Number of columns in domain
    :type ny:               Int
    :param nx:              Number of rows in domain
    :type  nx:              Int
    :param crop_id_all:     nt x nx x ny np array of current land cover
    :type crop_id_all:      Numpy Array
    :param crop_ids:        Num_crop x 1 np array of crop ids
    :type crop_ids:         Numpy Array
    :return:                Initial profits based on price signals
    :type:                  Numpy Array

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
