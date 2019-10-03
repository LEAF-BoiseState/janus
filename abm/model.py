"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""

import argparse
import os

import numpy as np

import abm.preprocessing.geofxns as gf
import abm.crop_functions.CropDecider as crpdec
import abm.initialize_agents_domain as init_agent
import abm.postprocessing.FigureFuncs as ppf
import abm.preprocessing.getNASSAgentData as get_nass

from abm.config_reader import ConfigReader


class Abm:

    def __init__(self, args=None, config_file=None):

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
        self.profit_act, self.profit_ant, self.profits = self.initialize_profit()

        # initialize agents
        self.agent_domain, self.agent_array = self.initialize_agents()

        # make agent decisions
        self.decisions()

        # update variables
        self.update()

        # save outputs
        self.save_outputs()

    def initialize_landscape_domain(self):
        """Initialize landscape and domain.

        :return:                        TODO:  add return descriptions for each variable

        """

        # select initial gcam data from initial year
        lc = gf.get_gcam(self.c.counties_shp, self.c.county_list, self.c.gcam_file)

        ny, nx = lc[0].shape

        # initialize minimum distance to city
        dist2city = gf.min_dist_city(lc)

        domain = init_agent.InitializeDomain(ny, nx)

        return lc, dist2city, domain, ny, nx

    def initialize_crops(self):
        """Initialize crops

        :return:                        TODO: add return descriptions for each variable

        """

        ag = np.where(self.c.key_file['SRB_cat'] == 'ag')

        crop_ids_load = np.int64(self.c.key_file['SRB_GCAM_id_list'][ag[0]])

        num_crops = len(crop_ids_load)

        crop_ids = crop_ids_load.reshape(num_crops, 1)

        crop_id_all = np.zeros((self.c.Nt, self.Ny, self.Nx))

        # TODO: this will be added into the cell class
        crop_id_all[0, :, :] = self.lc

        return crop_ids, crop_id_all, ag, num_crops

    def initialize_profit(self, unknown_var=30000.0, scale=1000.0):
        """Initialize profits.

        :return:                        TODO:  add return descriptions for each variable

        """

        profit_ant = np.zeros((self.c.Nt, self.Ny, self.Nx))

        # TODO: what is the unknown variable??  Where does scale in this case come from??
        profit_ant[0, :, :] = unknown_var + np.random.normal(loc=0.0, scale=scale, size=(1, self.Ny, self.Nx))

        profit_act = profit_ant.copy()

        profits = crpdec.GeneratePrices(self.c.Nt)[:, 0:self.c.Nc]

        return profit_act, profit_ant, profits

    def initialize_agents(self, id_field='ID', cat_header='SRB'):
        """Initialize agents.


        :return:                        TODO:  add return descriptions for each variable

        """

        # tenure from individual counties can also be used
        tenure = get_nass.TenureArea(id_field, self.c.nass_county_list, self.c.nass_year, self.c.agent_variables, self.c.nass_api_key)

        ages = get_nass.Ages(self.c.nass_year, id_field, self.c.nass_api_key)

        age_cdf = get_nass.makeAgeCDF(ages)

        tenure_cdf = get_nass.makeTenureCDF(tenure)

        agent_array = init_agent.PlaceAgents(self.Ny, self.Nx, self.lc, self.c.key_file, cat_header)

        agent_domain = init_agent.InitializeAgents(agent_array, self.domain, self.dist2city, tenure_cdf, age_cdf,
                                                   self.c.switch, self.Ny, self.Nx, self.lc, self.c.p)

        return agent_domain, agent_array

    def decisions(self):
        """Decision process.

        :return:                        TODO:  add return descriptions for each variable

        """
        for i in np.arange(1, self.c.Nt):

            for j in np.arange(self.Ny):

                for k in np.arange(self.Nx):

                    if self.agent_domain[j, k].FarmerAgents:

                        # Assess Profit
                        profit_last, profit_pred = crpdec.AssessProfit(self.crop_id_all[i - 1, j, k],
                                                                       self.profits[i - 1, :],
                                                                       self.profits[i, :],
                                                                       self.c.Nc,
                                                                       self.crop_ids)

                        # Decide on Crop
                        crop_choice, profit_choice = crpdec.DecideN(self.agent_domain[j, k].FarmerAgents[0].alpha,
                                                                      self.agent_domain[j, k].FarmerAgents[0].beta,
                                                                      self.c.fmin,
                                                                      self.c.fmax,
                                                                      self.c.n,
                                                                      profit_last,
                                                                      self.crop_ids,
                                                                      profit_pred,
                                                                      rule=True)

                        self.crop_id_all[i, j, k], self.profit_ant[i, j, k], self.profit_act[i, j, k] = crpdec.MakeChoice(
                                                                                            self.crop_id_all[i - 1, j, k],
                                                                                            profit_last,
                                                                                            self.profit_ant,
                                                                                            crop_choice,
                                                                                            profit_choice,
                                                                                            seed=False)

                        # move these indicies into the input variables
                        crop_choice, profit_choice = crpdec.DecideN(self.agent_domain[j, k].FarmerAgents[0].alpha,
                                                                  self.agent_domain[j, k].FarmerAgents[0].beta,
                                                                  self.c.fmin,
                                                                  self.c.fmax,
                                                                  self.c.n,
                                                                  profit_last,
                                                                  self.crop_ids,
                                                                  profit_pred,
                                                                  rule=True)

                        # is there a way to set this up so you can pass a NULL value or no value when seed=False?
                        self.crop_id_all[i, j, k], self.profit_ant[i, j, k], self.profit_act[i, j, k] = crpdec.MakeChoice(
                                                                                            self.crop_id_all[i - 1, j, k],
                                                                                            profit_last,
                                                                                            self.profit_ant,
                                                                                            crop_choice,
                                                                                            profit_choice,
                                                                                            seed=False)

        ppf.CropPerc(self.crop_id_all, self.crop_ids, self.c.Nt, self.c.Nc)

        # TODO:  where is FarmerAges used?
        FarmerAges = ppf.AgentAges(self.agent_domain, self.agent_array, self.Ny, self.Nx)

    def update(self):
        """Update agent variables.

        :return:

        """

        for i in np.arange(self.Ny):

            for j in np.arange(self.Nx):

                if self.agent_array[i][j]=='aFarmer':

                    self.agent_domain[i][j].FarmerAgents[0].UpdateAge()

                    # TODO:  are you overwriting the previous value?
                    self.agent_domain[i][j].FarmerAgents[0].UpdateDist2city(self.dist2city[i][j])

    def save_outputs(self):
        """Save outputs as NumPy arrays.

        :return:

        """

        out_file = os.path.join(self.c.output_dir, '{}_{}_m_{}_yr.npy')

        # save timeseries of landcover coverage
        np.save(out_file.format('landcover', self.c.scale, self.c.Nt), self.crop_id_all)

        # save timeseries of profits
        np.save(out_file.format('profits', self.c.scale, self.c.Nt), self.profit_act)

        # save domain, can be used for initialization
        np.save(out_file.format('domain', self.c.scale, self.c.Nt), self.domain)


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

    Abm(args)

    # Abm('/Users/d3y010/repos/github/IM3-BoiseState/example/config.yml')