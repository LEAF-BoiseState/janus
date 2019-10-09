"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""

import argparse
import os

import numpy as np

import janus.preprocessing.geofxns as gf
import janus.crop_functions.crop_decider as crpdec
import janus.initialize_agents_domain as init_agent
import janus.postprocessing.create_figures as ppf
import janus.preprocessing.get_nass_agent_data as get_nass

from janus.config_reader import ConfigReader


class Janus:

    def __init__(self, config_file=None, args=None):

        if (args is not None) and (config_file is None):

            # if config file used, read it in; else, use args from user
            try:
                self.c = ConfigReader(args.config_file)

            except AttributeError:
                self.c = args

        else:

            self.c = ConfigReader(config_file)

        # initialize landscape and domain
        self.lc, self.dist2city, self.domain, self.Ny, self.Nx = self.initialize_landscape_domain()

        # initialize crops
        self.crop_ids, self.crop_id_all, self.ag, self.num_crops = self.initialize_crops()

        # initialize profits
        self.profits_actual, self.profit_signals = self.initialize_profit()

        # initialize agents
        self.agent_domain, self.agent_array = self.initialize_agents()

        # make agent decisions
        self.decisions()

        # save outputs
        self.save_outputs()

    def initialize_landscape_domain(self):
        """Initialize landscape and domain.

        :return: lc
        :return: dist2city
        :return: domain
        :return: ny
        :return: nx
        """

        # select initial gcam data from initial year
        lc = gf.get_gcam(self.c.counties_shp, self.c.county_list, self.c.gcam_file)

        ny, nx = lc[0].shape

        # initialize minimum distance to city
        dist2city = gf.min_dist_city(lc)

        domain = init_agent.initialize_domain(ny, nx)

        return lc, dist2city, domain, ny, nx

    def initialize_crops(self):
        """Initialize crops

        :return:                        TODO: add return descriptions for each variable

        """

        ag = np.where(self.c.key_file['local_cat'] == 'ag')

        crop_ids_load = np.int64(self.c.key_file['local_GCAM_id_list'][ag[0]])

        num_crops = len(crop_ids_load)

        crop_ids = crop_ids_load.reshape(num_crops, 1)

        crop_id_all = np.zeros((self.c.Nt, self.Ny, self.Nx))

        # TODO: this will be added into the cell class
        crop_id_all[0, :, :] = self.lc

        return crop_ids, crop_id_all, ag, num_crops

    def initialize_profit(self):
        """Initialize profits.

        :return:                        TODO:  add return descriptions for each variable

        """

        # initializes profits based on profit signals from csv output from generate synthetic prices
        profit_signals = np.transpose(self.c.profits_file.as_matrix())

        assert np.all([profit_signals[:, 0], self.crop_ids[:, 0]]), 'Crop IDs in profit signals do not match Crop IDs from landcover'

        profit_signals = profit_signals[:, 1:]

        assert profit_signals.shape[1] == self.c.Nt, 'The number of timesteps in the profit signals do not match the number of model timesteps'

        profits_actual = init_agent.profits(profit_signals, self.c.Nt, self.Ny, self.Nx, self.crop_id_all, self.crop_ids)

        return profits_actual, profit_signals

    def initialize_agents(self, id_field='ID', cat_option='local'):
        """Initialize agents.


        :return:                        TODO:  add return descriptions for each variable

        """

        tenure = get_nass.tenure_area(id_field, self.c.nass_county_list, self.c.nass_year, self.c.agent_variables, self.c.nass_api_key)

        ages = get_nass.ages(self.c.nass_year, id_field, self.c.nass_api_key)

        age_cdf = get_nass.make_age_cdf(ages)

        tenure_cdf = get_nass.make_tenure_cdf(tenure)

        agent_array = init_agent.place_agents(self.Ny, self.Nx, self.lc, self.c.key_file, cat_option)

        # replace
        agent_domain = init_agent.agents(agent_array, self.domain, self.dist2city, tenure_cdf, age_cdf, self.c.switch,
                                         self.Ny, self.Nx, self.lc, self.c.p)

        return agent_domain, agent_array

    def decisions(self):
        """Decision process.

        :return:                        TODO:  add return descriptions for each variable

        """
        for i in np.arange(1, self.c.Nt):

            for j in np.arange(self.Ny):

                for k in np.arange(self.Nx):

                    if self.agent_domain[j, k].FarmerAgents:

                        # assess Profit
                        profit_last, profit_pred = crpdec.assess_profit(self.crop_id_all[i-1, j, k],
                                                                       self.profits_actual[i-1, j, k],
                                                                       self.profit_signals[:, i],
                                                                       self.num_crops,
                                                                       self.crop_ids)

                        # choose between crops
                        crop_choice, profit_choice = crpdec.decide_n(self.agent_domain[j, k].FarmerAgents[0].alpha,
                                                                    self.agent_domain[j, k].FarmerAgents[0].beta,
                                                                    self.c.fmin,
                                                                    self.c.fmax,
                                                                    self.c.n,
                                                                    profit_last,
                                                                    self.crop_ids,
                                                                    profit_pred,
                                                                    rule=True)

                        # decide whether to switch and add random variation to actual profit
                        self.crop_id_all[i, j, k], self.profits_actual[i, j, k] = crpdec.make_choice(self.crop_id_all[i-1, j, k],
                                                                                                    profit_last,
                                                                                                    crop_choice,
                                                                                                    profit_choice,
                                                                                                    seed=False)

                        # update agent attributes
                        self.agent_domain[j, k].FarmerAgents[0].update_age()

        ppf.plot_crop_percent(self.crop_id_all, self.crop_ids, self.c.Nt, self.num_crops, self.c.scale,
                              self.c.output_dir, self.c.key_file, self.ag)

        # TODO:  this currently has no output that is saved
        ppf.plot_agent_ages(self.agent_domain, self.agent_array, self.Ny, self.Nx)

    def save_outputs(self):
        """Save outputs as NumPy arrays.

        :return:

        """
        out_file = os.path.join(self.c.output_dir, '{}_{}m_{}yr.npy')

        # save time series of landcover coverage
        np.save(out_file.format('landcover', self.c.scale, self.c.Nt), self.crop_id_all)

        # save time series of profits
        np.save(out_file.format('profits', self.c.scale, self.c.Nt), self.profits_actual)

        # save domain, can be used for initialization
        np.save(out_file.format('domain', self.c.scale, self.c.Nt), self.agent_domain)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config_file', type=str, help='Full path with file name and extension to YAML configuration file.')
    parser.add_argument('-shp', '--f_counties_shp', type=str, help='Full path with file name and extension to the input counties shapefile.')
    parser.add_argument('-key', '--f_key_file', type=str, help='Full path with file name and extension to the input land class category key file.')
    parser.add_argument('-gcam', '--f_gcam_file', type=str, help='Full path with file name and extension to the input GCAM raster file.')
    parser.add_argument('-s', '--switch_params', type=list, help='List of lists for switching averse, tolerant parameters (alpha, beta)')
    parser.add_argument('-nt', '--nt', type=int, help='Need description')
    parser.add_argument('-nc', '--nc', type=int, help='Need description')
    parser.add_argument('-fmin', '--fmin', type=float, help='Need description')
    parser.add_argument('-fmax', '--fmax', type=float, help='Need description')
    parser.add_argument('-f0', '--f0', type=float, help='Need description')
    parser.add_argument('-n', '--n', type=int, help='Need description')
    parser.add_argument('-seed', '--crop_seed_size', type=int, help='Need description')
    parser.add_argument('-yr', '--target_yr', type=int, help='Need description')
    parser.add_argument('-sc', '--scale', type=int, help='Need description')
    parser.add_argument('-cl', '--county_list', type=list, help='List of county names to evaluate from the input shapefile.')
    parser.add_argument('-av', '--agent_variables', type=list, help='Need description')
    parser.add_argument('-nyr', '--nass_year', type=int, help='Need description')
    parser.add_argument('-ncy', '--nass_county_list', type=list, help='Need description')
    parser.add_argument('-api', '--nass_api_key', type=int, help='Need description')

    args = parser.parse_args()

    Janus(args)
