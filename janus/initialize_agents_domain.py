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
    """ Create empty domain array

    :param ny:  Number of columns in domain
    :type ny:   Int

    :param nx:  Number of rows in domain
    :type nx:   Int

    :return:    Empty numpy array filled with class Dcell at each pixel
    :type:      Numpy Array
    """
    domain = np.empty((ny, nx), dtype=object)

    for i in np.arange(ny):

        for j in np.arange(nx):

            domain[i][j] = cell.Dcell()

    return domain


def place_agents(ny, nx, lc, key_file, cat_option):
    """ Place agents on the landscape based on land cover and associated categorization

    :param ny:          Number of columns in domain
    :type ny:           Int
    
    :param nx:          Number of rows in domain
    :type ny:           Int
    
    :param lc:          Initial land cover numpy array
    :type lc:           Numpy Array
    
    :param key_file:    csv file with categorization from CDL categories to GCAM or user defined categories, see README file.
    :type key_file:     CSV file
    
    :param cat_option:  Set whether using 'GCAM' or 'local'categorization. If the local characterization has been changed to 
                        have more or less categories, the number of rows to use in line 52/53 will need to be edited
    :type cat_option:   String

    :return:            numpy array of strings with each agent type
    :type:              Numpy Array

    """
    agent_array = np.empty((ny, nx), dtype='U10')

    if cat_option == 'local':
        
        agent_cat = key_file['local_cat'][0:28]
        code = key_file['local_GCAM_id_list'][0:28]

    elif cat_option == 'GCAM':

        agent_cat = key_file['GCAM_cat'][0:24]
        code = key_file['GCAM_id_list'][0:24]

    ag = np.array(code[agent_cat == 'ag']).astype(int)
    urb = np.array(code[agent_cat == 'urb']).astype(int)
    water = np.array(code[agent_cat == 'water']).astype(int)
    empty = np.array(code[agent_cat == 'nat']).astype(int)

    # this works, would be better without the for loops
    for i in ag:
        agent_array[lc[0] == i] = farmer.Farmer.__name__

    for i in water:
        agent_array[lc[0] == i] = 'water'

    for i in urb:
        agent_array[lc[0] == i] = urban.Urban.__name__

    for i in empty:
        agent_array[lc[0] == i] = 'empty'

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
    for i in np.arange(ny):

        for j in np.arange(nx):

            if agent_array[i][j] == farmer.Farmer.__name__:

                agent_data = getNASS.farmer_data(tenure_cdf, age_cdf, switch, dist2city[i][j], p, attr)
                new_agent = farmer.Farmer(Age=agent_data["AgeInit"], LandStatus=agent_data["LandStatus"],
                                          Dist2city=agent_data["Dist2city"], nFields=agent_data['nFields'],
                                          alpha=agent_data['Alpha'],
                                          beta=agent_data['Beta'])  # this is passing actual agent data
                domain[i][j].add_agent(new_agent)

            if agent_array[i][j] == urban.Urban.__name__:

                agent_data = getNASS.urban_data(lc[0][i][j])
                new_agent = urban.Urban(density=agent_data["Density"])
                domain[i][j].add_agent(new_agent)

    return domain


def init_profits(profit_signals, nt, ny, nx, crop_id_all, crop_ids):
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

            crop_ind = crop_id_all[0, i, j]
            crop_ix = np.where(crop_ids == crop_ind)

            if crop_ind in crop_ids:
                profits_actual[0, i, j] = profit_signals[crop_ix[0][0], 0]

            else:
                profits_actual[0, i, j] = 0

    return profits_actual
