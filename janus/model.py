"""
Agent Based Model of Land Use and Land Cover Change

@author: lejoflores, kendrakaiser & hollybossart

@license: BSD 2-Clause
"""

import argparse
import os

# this is for the saving dict file output
import pickle

import numpy as np
import gdal

import janus.preprocessing.geofxns as gf
import janus.crop_functions.crop_decider as crpdec
import janus.initialize_agents_domain as init_agent
import janus.postprocessing.create_figures as ppf
import janus.preprocessing.get_nass_agent_data as get_nass
import janus.crop_functions.networks as nwks

from janus.config_reader import ConfigReader


class Janus:

    def __init__(self, config_file=None, args=None, save_result=True, plot_results=False):

        if (args is not None) and (config_file is None):

            # if config file used, read it in; else, use args from user
            try:
                self.c = ConfigReader(args.config_file)

            except AttributeError:
                self.c = args

            except TypeError:
                raise TypeError("Must pass either a configuration file or required parameters.")

        elif (args is None) and (config_file is None):

            raise RuntimeError("Must pass either a configuration file or required parameters.")

        else:

            self.c = ConfigReader(config_file)

        # initialize landscape and domain
        self.lc, self.dist2city, self.domain, self.Ny, self.Nx = self.initialize_landscape_domain()

        # initialize crops
        self.crop_ids, self.crop_id_all, self.ag, self.num_crops, self.lc_stats = self.initialize_crops()

        # initialize profits
        self.profits_actual, self.profit_signals = self.initialize_profit()

        # initialize agents
        self.agent_domain, self.agent_array, self.agentID_list, self.agentIX = self.initialize_agents()

        # network will be stored as a dictionary here
        self.network = self.initialize_network()

        # make agent decisions
        self.decisions()


        # plot results
        if plot_results:
            self.plot_results()

        # save outputs
        if save_result:
            self.save_outputs()

    def initialize_landscape_domain(self):
        """Initialize landscape and domain.

        :return: lc, numpy array of land cover categories within domain at scale of interest
        :return: dist2city, numpy array of distance to nearest city cell
        :return: domain, grid of dCell classes
        :return: ny, number of rows in domain
        :return: nx, number of columns in domain
        """

        # import the initial land cover data
        lc_raster = gdal.Open(self.c.f_init_lc_file)
        lc = lc_raster.GetRasterBand(1).ReadAsArray()

        ny = lc_raster.RasterYSize
        nx = lc_raster.RasterXSize

        # initialize minimum distance to city
        dist2city = gf.min_dist_city(lc)

        domain = init_agent.initialize_domain(ny, nx)

        return lc, dist2city, domain, ny, nx

    def initialize_crops(self):
        """Initialize crops

        :return: crop_ids, numpy array of the crop IDs that are in the domain
        :return: crop_id_all, numpy array of land cover categories through time
        :return: ag, numpy array of where agricultural cells exist in the domain
        :return: num_crops, integer og the number of crops being assessed

        """

        ag = np.where(self.c.key_file['local_cat'] == 'ag')

        crop_ids_load = np.int64(self.c.key_file['local_GCAM_id_list'][ag[0]])

        num_crops = len(crop_ids_load)

        crop_ids = crop_ids_load.reshape(num_crops, 1)

        crop_id_all = np.zeros((self.c.Nt, self.Ny, self.Nx))

        crop_id_all[0, :, :] = self.lc

        # save output stats
        lc_stats = np.zeros((num_crops, self.Ny+1))
        lc_stats[:, 0] = crop_ids_load

        return crop_ids, crop_id_all, ag, num_crops, lc_stats

    def initialize_profit(self):
        """Initialize profits based on profit signals csv that is either generated or input from other model output

        :return:    [0] Numpy Array; profits_actual, profit signal with a random variation
                    [1] Numpy Array; profit_signals, transposed profit signals cleaned to be used in other functions
        """
        if self.c.profits == 'generated':

            profit_signals = np.transpose(self.c.profits_file.values)

            assert np.all([profit_signals[:, 0], self.crop_ids[:, 0]]), 'Crop IDs in profit signals do not match ' \
                                                                        'Crop IDs from land cover'
            profit_signals = profit_signals[:, 1:]

        elif self.c.profits == 'gcam':
            profit_signals = np.transpose(self.c.gcam_profits_file.values)
        else:
            print("Profit type not supported")

        assert profit_signals.shape[1] == self.c.Nt, 'The number of time steps in the profit signals do not ' \
                                                     'match the number of model time steps'

        profits_actual = init_agent.init_profits(profit_signals, self.c.Nt, self.Ny, self.Nx, self.crop_id_all,
                                                 self.crop_ids)

        return profits_actual, profit_signals

    def initialize_agents(self):
        """Initialize agents based on NASS data and initial land cover

        :return agent domain:   [0] Numpy array; agent_domain, domain with agent cell classes filled with agent info
                                [1] Numpy array; agent_array, strings that define which agent is in each location
                                [2] Numpy array; agentID_list, array of all agent IDs (i*ny+j)

        """

        tenure = get_nass.tenure_area(self.c.state, self.c.nass_county_list, self.c.nass_year, self.c.agent_variables,
                                      self.c.nass_api_key)

        ages = get_nass.ages(self.c.nass_year, self.c.state, self.c.nass_api_key)

        age_cdf = get_nass.make_age_cdf(ages)

        tenure_cdf = get_nass.make_tenure_cdf(tenure)

        agent_array = init_agent.place_agents(self.Ny, self.Nx, self.lc, self.c.key_file, self.c.cat_option)

        agent_domain, agentID_list, agentIX = init_agent.agents(agent_array, self.domain, self.dist2city, tenure_cdf, age_cdf,
                                                       self.c.switch, self.Ny, self.Nx, self.lc, self.c.p, self.c.attr)

        return agent_domain, agent_array, agentID_list, agentIX



    def initialize_network(self):
        """ This will create and return a network based upon which type of network
        was listed in the config.yml file. Network type must be properly set in
        config.yml to be either: randomwalk, erdosrenyi, barabasi, smallworld,
        or gilbert.
        
        :return: network_dict is dictionary where the keys are all
        agentIDs and the value associated with that key is a numpy array
        containing the agentIDs that share a connection with the key agent.

        """

        if self.c.network == 'randomwalk':
            # TODO: if this is the case there need to be more parameters than what
            # are included here. See notes in the network library
            # For now, a user could use the jupyter notebook to determine a max number
            # of steps based on the metric they care about
            # the 'arbitrary' values are all currently hard coded but need to be placed in config file

            arbitrary_time_steps = 10
            arbitrary_torus_option = True
            agent_network = nwks.generate_random_walk(self.Nx - 1, self.Ny - 1, self.agentID_list,
                                                      arbitrary_torus_option, arbitrary_time_steps)
            print(list(agent_network[122].keys()))
        if self.c.network == 'erdosrenyi':
            # if this is the case, there needs to be an extra parameter
            # this parameter for erdos renyi is defined as the probability that 
            # a given agent will form a connection -- this will need to be supplied
            # by the user in config file. For now it is arbitrary

            # TODO: change this from hard coded to a config file option
            arbitrary_prob = 0.1
            agent_network = nwks.generate_erdos_renyi(self.agentID_list, arbitrary_prob)

        if self.c.network == 'barabasi':
            # TODO: change this from hard coded to a config file option
            # for more information on what the parameters could be, see README in im3agents library repo
            arbitrary_edge_number = 2 * len(self.agentID_list) / 5
            agent_network = nwks.generate_barabasi_alberts(self.agentID_list, arbitrary_edge_number)

        if self.c.network == 'smallworld':
            # TODO: change this from hard coded to a config file options
            # see README link to networkx documentation
            arbitrary_neighbors = 3
            arbitrary_rewire_prob = 0.5
            agent_network = nwks.generate_small_world(self.agentID_list, arbitrary_neighbors, arbitrary_rewire_prob)

        return agent_network

    def decisions(self):
        """Decision process.

        :return:    Updated domain with agent information and land cover choice

        """

        for i in np.arange(1, self.c.Nt):

            for j in np.arange(self.Ny):

                for k in np.arange(self.Nx):

                    if self.agent_domain[j, k].FarmerAgents:

                        # make crop choice based on decision making process

                        if self.c.decision_type == 'profit':
                            # assess profit - only needs to occur for profit based learning
                            profit_last, profit_pred = crpdec.assess_profit(self.crop_id_all[i - 1, j, k],
                                                                            # this is the crop for last time step for agent jk
                                                                            self.profits_actual[i - 1, j, k],
                                                                            # this is last profit for agent jk
                                                                            self.profit_signals[:, i],
                                                                            self.num_crops,
                                                                            self.crop_ids)

                            # identify the most profitable crop
                            crop_choice, profit_choice = crpdec.profit_maximizer(
                                self.agent_domain[j, k].FarmerAgents[0].alpha,
                                self.agent_domain[j, k].FarmerAgents[0].beta,
                                self.c.fmin,
                                self.c.fmax,
                                self.c.n,
                                profit_last,
                                self.crop_ids,
                                profit_pred,
                                rule=True)

                            # decide whether to switch and add random variation to actual profit
                            self.crop_id_all[i, j, k], self.profits_actual[i, j, k] = crpdec.make_choice(
                                self.crop_id_all[i - 1, j, k],
                                profit_last,
                                crop_choice,
                                profit_choice,
                                seed=False)

                        if self.c.decision_type == 'success':
                            # retrieve the cropIDs and the associated profits of their network
                            network_profits = crpdec.retrieve_network_profits(self.profits_actual[i - 1, :, :],
                                                                              self.crop_id_all[i - 1, :, :],
                                                                              self.network[
                                                                                  self.agent_domain[j, k].FarmerAgents[
                                                                                      0].agentID], self.agentIX)

                            # identify the most profitable crop of the network
                            # if the following were combined it could be: crop_choice, profit_choice = crpdec.success_bias_crop()
                            # if all three learning strategies are using assess_profit / profit_maximizer/ make_choice,
                            # those could be outside of if statement to reduce duplicate code
                            len_prof = len(network_profits)
                            profit_last, profit_pred = crpdec.assess_profit(self.crop_id_all[i - 1, j, k],
                                                                            self.profits_actual[i - 1, j, k],
                                                                            network_profits[:, 1],
                                                                            len_prof,
                                                                            network_profits[:, 0])

                            # identify the most profitable crop
                            crop_choice, profit_choice = crpdec.profit_maximizer(
                                self.agent_domain[j, k].FarmerAgents[0].alpha,
                                self.agent_domain[j, k].FarmerAgents[0].beta,
                                self.c.fmin, self.c.fmax, self.c.n, profit_last,
                                network_profits[:, 1].reshape((len_prof, 1)), profit_pred, rule=True)

                            # decide whether to switch and add random variation to actual profit
                            self.crop_id_all[i, j, k], self.profits_actual[i, j, k] = crpdec.make_choice(
                                self.crop_id_all[i - 1, j, k],
                                profit_last,
                                crop_choice,
                                profit_choice,
                                seed=False)

                        # if decision_type = 'conformist':

                        # update agent attributes
                        self.agent_domain[j, k].FarmerAgents[0].update_age()

            # Save count of each land cover to 2D array for export
            unique_crops, crop_counts = np.unique(self.crop_id_all[i, :, :].astype(int)[self.crop_id_all[i, :, :] < 30], return_counts=True)
            #print(i, unique_crops)
            ix = self.lc_stats[:, 0].astype(int).searchsorted(unique_crops)
            self.lc_stats[ix, i] = crop_counts

    def plot_results(self):
        """Create result plots and save them."""

        ppf.plot_crop_percent(self.crop_id_all, self.crop_ids, self.c.Nt, self.num_crops, self.c.scale,
                              self.c.output_dir, self.c.key_file, self.ag)

        ppf.plot_agent_ages(self.agent_domain, self.agent_array, self.Ny, self.Nx, self.c.Nt,
                            self.c.scale, self.c.output_dir)

    def save_outputs(self):
        """Save outputs as NumPy arrays.

        The dimensions of each output NumPy array are [Number of time steps, Ny, Nx]
        """

        out_file = os.path.join(self.c.output_dir, '{}_{}m_{}yr.npy')
        #  save time series of land cover coverage
        np.save(out_file.format('lc_percent', self.c.scale, self.c.Nt), self.lc_stats)

        # save time series of land cover coverage
        #np.save(out_file.format('landcover', self.c.scale, self.c.Nt), self.crop_id_all)

        # save time series of profits
        #np.save(out_file.format('profits', self.c.scale, self.c.Nt), self.profits_actual)

        # save domain, can be used for initialization
        #np.save(out_file.format('domain', self.c.scale, self.c.Nt), self.agent_domain)

        # save dictionary of network
        # TODO: currently outputting using pickle but network is not human readable
        # it is possible here to use JSON format but that might be less straightforward to read in
        #nwk_out = open(os.path.join(self.c.output_dir,'network.pk1'), 'wb')
        #pickle.dump(self.network, nwk_out)
        #nwk_out.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config_file', type=str,
                        help='Full path with file name and extension to YAML configuration file.')
    parser.add_argument('-shp', '--f_counties_shp', type=str,
                        help='Full path with file name and extension to the input counties shapefile.')
    parser.add_argument('-key', '--f_key_file', type=str,
                        help='Full path with file name and extension to the input land class category key file.')
    parser.add_argument('-gcam', '--f_gcam_profits_file', type=str,
                        help='Full path with file name and extension to the input GCAM raster file.')
    parser.add_argument('-s', '--switch_params', type=list,
                        help='List of lists for switching averse, tolerant parameters (alpha, beta)')
    parser.add_argument('-nt', '--nt', type=int, help='Number of timesteps')

    # TODO: add in arguments for network creations and decision type

    # TODO: number of crops is calculated after doing the GIS pre-processing, if nc is needed for price generation, we might need to adjust this
    parser.add_argument('-nc', '--nc', type=int, help='Number of crops')
    parser.add_argument('-fmin', '--fmin', type=float,
                        help='The fraction of current profit at which the CDF of the beta distribution is zero')
    parser.add_argument('-fmax', '--fmax', type=float,
                        help='The fraction of current profit at which the CDF of the beta distribution is one')
    parser.add_argument('-n', '--n', type=int, help='The number of points to generate in the CDF')
    parser.add_argument('-seed', '--crop_seed_size', type=int,
                        help='Seed to set for random number generators for unit testing')
    parser.add_argument('-yr', '--initalization_yr', type=int,
                        help='Initialization year assocciated with landcover input')
    parser.add_argument('-state', '--state', type=str, help='State where NASS data is pulled from, capitalized acronym')
    parser.add_argument('-sc', '--scale', type=int,
                        help='Scale of landcover grid in meters. Current options are 1000 and 3000 m')
    parser.add_argument('-av', '--agent_variables', type=list,
                        help='NASS variables to characterize agents with. Currently set to use "TENURE" and "AREA OPERATED"')
    parser.add_argument('-nyr', '--nass_year', type=int,
                        help='Year that NASS data are pulled from. This data is collected every 5 years, with the inital year here being 2007')
    parser.add_argument('-ncy', '--nass_county_list', type=list,
                        help='List of counties in the domain that NASS data is collected from, these have to be entirely capatalized')
    parser.add_argument('-api', '--nass_api_key', type=int,
                        help='A NASS API is needed to access the NASS data, get yours here https://quickstats.nass.usda.gov/api')

    args = parser.parse_args()

    Janus(args=args)
