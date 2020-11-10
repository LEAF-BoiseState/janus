"""
Created on Mon Aug 12 11:15:12 2019

@author: kek25
"""
import numpy as np

import janus.agents.farmer as farmer
import janus.agents.d_cell as cell
import janus.agents.urban as urban
import janus.preprocessing.get_nass_agent_data as getNASS


def initialize_domain(ny, nx):
    """

    :param ny: Number of columns in domain
    :param nx: Number of rows in domain

    :return: empty numpy array filled with class Dcell at each pixel

    """
    domain = np.empty((ny, nx), dtype=object)

    for i in np.arange(ny):

        for j in np.arange(nx):

            domain[i][j] = cell.Dcell()

    return domain


def place_agents(ny, nx, lc, key_file, cat_option):
    """ Place agents on the landscape based on landcover and associated categorization

    :param ny: Number of columns in domain
    :param nx: Number of rows in domain
    :param lc: Initial landcover numpy array
    :param key_file: csv file with categorization from CDL categories to GCAM or user defined categories, see README file.
    :param cat_option:  Set whether using 'GCAM' or 'local'categorization. If the local caracterization has been changed to
    have more or less categories, the number of rows to use in line 52/53 will need to be edited

    :return: numpy array of strings with each agent type

    """
    agent_array = np.empty((ny, nx), dtype='U10')

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
        agent_array[lc == i] = farmer.Farmer.__name__

    for i in water:
        agent_array[lc == i] = 'water'

    for i in urb:
        agent_array[lc == i] = urban.Urban.__name__

    for i in empty:
        agent_array[lc == i] = 'empty'

    return agent_array


def agents(agent_array, domain, dist2city, tenure_cdf, age_cdf, switch, ny, nx, lc, p, attr):
    """Place agent structures onto landscape and define attributes.

    :param agent_array: Numpy array of strings defining each agent type
    :type agent_array:  Numpy Array
    
    :param domain:      Initial domain filled with class Dcell
    :type domain:       Numpy Array
    
    :param dist2city:   Numpy array of distance to city (float)
    :type dist2city:    Numpy Array
    
    :param tenure_cdf:  CDF of tenure type in the domain
    :type tenure_cdf:
    
    :param age_cdf:     CDF of ages in the domain
    :type age_cdf:
    
    :param switch:      List of lists of parameter sets to describe agent switching behavior
    :type switch:       List
    
    :param ny:          Number of columns in domain
    :type ny:           Int
    
    :param nx:          Number of rows in domain
    :type nx:           Int
    
    :param lc:          Initial land cover numpy array
    :type lc:           Numpy Array
    
    :param p:           Percentage of switching averse farming agents
    :type p:            Float
    
    :param attr:        A boolean indicating whether or not to use switching curves based on tenure and age attributes
    :type attr:         Bool
    
    :return:            Domain with agents in each dCell
    :type:              Numpy Array
    
    """
    farmer_agent_list = []
    agentIX =[]
    for i in np.arange(ny):

        for j in np.arange(nx):

            if agent_array[i][j] == farmer.Farmer.__name__:
                
                AgentData = getNASS.farmer_data(tenure_cdf, age_cdf, switch, dist2city[i][j], p, attr)
                NewAgent = farmer.Farmer(Age=AgentData["AgeInit"], LandStatus=AgentData["LandStatus"],
                                          LocationID =(i, j),
                                          Dist2city=AgentData["Dist2city"], nFields=AgentData['nFields'],
                                          alpha=AgentData['Alpha'],
                                          beta=AgentData['Beta'],
                                          agentID=i*ny+j)

                domain[i][j].add_agent(NewAgent)
                farmer_agent_list.append(NewAgent.agentID)
                agentIX.append(np.array([NewAgent.agentID, i, j]))

            if agent_array[i][j] == urban.Urban.__name__:

                AgentData = getNASS.urban_data(lc[i][j])
                NewAgent = urban.Urban(density=AgentData["Density"])
                domain[i][j].add_agent(NewAgent)

    return domain, farmer_agent_list, agentIX


def init_profits(profit_signals, nt, ny, nx, CropID_all, CropIDs):
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

    profits_actual = np.zeros((nt, ny, nx))

    for i in np.arange(ny):

        for j in np.arange(nx):

            CropInd = CropID_all[0, i, j]
            CropIx = np.where(CropIDs == CropInd)

            if CropInd in (CropIDs):
                profits_actual[0, i, j] = profit_signals[CropIx[0][0], 0]

            else:
                profits_actual[0, i, j] = 0

    return profits_actual
