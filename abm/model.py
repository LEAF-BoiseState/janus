"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""

import numpy as np
import geopandas as gp
import yaml

import abm.preprocessing.geofxns as gf
import abm.crop_functions.CropDecider as crpdec
import abm.initialize_agents_domain as init_agent
import abm.postprocessing.FigureFuncs as ppf
import abm.preprocessing.getNASSAgentData as get_nass


class Abm:

    def __init__(self, config_file):

        c = self.config_reader(config_file)

        self.counties_shp = gp.read_file(c['f_counties_shp'])
        self.counties_shp.set_index('county', inplace=True)

        self.key_file = gp.read_file(c['f_key_file'], sep=',')

        self.gcam_file = c['gcam_file']

        self.Nt = c['nt']

        # TODO: there are actually 17 when the 1km is run, need random profit profiles for each of these
        self.Nc = c['nc']

        # set agent switching parameters (alpha, beta) [[switching averse], [switching tolerant]]
        self.switch = np.array(c['switch_params'])

        # proportion of each switching type, lower than p is averse, higher is tolerant
        self.p = c['p']

        # Max and min .... total Profit, percent profit?
        self.fmin = c['fmin']
        self.fmax = c['fmax']
        self.f0 = c['f0']
        self.n = c['n']

        # TODO:  define seed for crop decider; This is not used in this script but is set as `global`
        crpdec.DefineSeed(c['crop_seed_size'])

        # target year
        self.target_year = c['target_yr']

        # scale of grid in meters
        self.scale = c['scale']

        # list of counties to evaluate
        self.county_list = c['county_list']

        # agent variables
        self.agent_variables = c['agent_variables']

        # NASS year
        self.nass_year = c['nass_year']

        # NASS county list
        self.nass_county_list = [i.upper() for i in c['nass_county_list']]

        # initialize landscape and domain
        self.lc, self.dist2city, self.domain, self.Ny, self.Nx = self.initialize_landscape_domain()

        # initialize crops
        self.crop_ids, self.crop_id_all = self.initialize_crops()

        # initialize profits
        self.profit_act, self.profit_ant, self.profits = self.initialize_profit()

        # initialize agents
        self.agent_domain, self.agent_array = self.initialize_agents()

        # make agent decisions
        self.decisions()

        # update variables
        self.update()

        # save output
        self.save_output()

    @staticmethod
    def config_reader(config_file):
        """Read the YAML config file to a dictionary.

        :param config_file:             Full path with file name and extension to the input config file.

        :return:                        YAML dictionary-like object

        """

        with open(config_file) as f:
            return yaml.safe_load(f)

    def initialize_landscape_domain(self):
        """Initialize landscape and domain.

        :return:                        TODO:  add return descriptions for each variable

        """

        # select initial gcam data from initial year
        lc = gf.get_gcam(self.counties_shp, self.county_list, self.gcam_file)

        ny, nx = lc[0].shape

        # initialize minimum distance to city
        dist2city = gf.min_dist_city(lc)

        domain = init_agent.InitializeDomain(ny, nx)

        return lc, dist2city, domain, ny, nx

    def initialize_crops(self):
        """Initialize crops

        :return:                        TODO: add return descriptions for each variable

        """

        # TODO: need to make this automatic depending on which crops show up (which of AllCropIDs == np.unique(lc))
        crop_ids = np.array([1, 2, 3, 10]).reshape(self.Nc, 1)

        crop_id_all = np.zeros((self.Nt, self.Ny, self.Nx))

        # TODO: this will be added into the cell class
        crop_id_all[0, :, :] = self.lc

        return crop_ids, crop_id_all

    def initialize_profit(self, unknown_var=30000.0, scale=1000.0):
        """Initialize profits.

        :return:                        TODO:  add return descriptions for each variable

        """

        profit_ant = np.zeros((self.Nt, self.Ny, self.Nx))

        # TODO: what is the unknown variable??  Where does scale in this case come from??
        profit_ant[0, :, :] = unknown_var + np.random.normal(loc=0.0, scale=scale, size=(1, self.Ny, self.Nx))

        profit_act = profit_ant.copy()

        profits = crpdec.GeneratePrices(self.Nt)[:, 0:self.Nc]

        return profit_act, profit_ant, profits

    def initialize_agents(self, id_field='ID', cat_header='SRB'):
        """Initialize agents.


        :return:                        TODO:  add return descriptions for each variable

        """

        # tenure from individual counties can also be used
        tenure = get_nass.TenureArea(id_field, self.nass_county_list, self.nass_year, self.agent_variables)

        ages = get_nass.Ages(self.nass_year, id_field)

        age_cdf = get_nass.makeAgeCDF(ages)

        tenure_cdf = get_nass.makeTenureCDF(tenure)

        agent_array = init_agent.PlaceAgents(self.Ny, self.Nx, self.lc, self.key_file, cat_header)

        agent_domain = init_agent.InitializeAgents(agent_array, self.domain, self.dist2city, tenure_cdf, age_cdf,
                                                   self.switch, self.Ny, self.Nx, self.lc, self.p)

        return agent_domain, agent_array

    def decisions(self):
        """Decision process.

        :return:                        TODO:  add return descriptions for each variable

        """

        for i in np.arange(1, self.Nt):

            for j in np.arange(self.Ny):

                for k in np.arange(self.Nx):

                    if self.agent_domain[j, k].FarmerAgents:

                        # Assess Profit
                        profit_last, profit_pred = crpdec.AssessProfit(self.crop_id_all[i - 1, j, k],
                                                                       self.profits[i - 1, :],
                                                                       self.profits[i, :],
                                                                       self.Nc,
                                                                       self.crop_ids)

                        # Decide on Crop
                        crop_choice, profit_choice = crpdec.DecideN(self.agent_domain[j, k].FarmerAgents[0].alpha,
                                                                      self.agent_domain[j, k].FarmerAgents[0].beta,
                                                                      self.fmin,
                                                                      self.fmax,
                                                                      self.n,
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
                                                                  self.fmin,
                                                                  self.fmax,
                                                                  self.n,
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

        ppf.CropPerc(self.crop_id_all, self.crop_ids, self.Nt, self.Nc)

        # crop_id_all, profit_ant, profit_act = cd.MakeDecision(Nt, Ny, Nx, Nc, crop_id_all, profits, profit_ant,
        # profit_act, a_ra, b_ra, fmin, fmax, n, crop_ids)

        # one unit test would be to confirm that non-ag stayed the same and that all of the ag did not stay the same"
        # need to pull out the parts that dont rely on the loop and put the decision inside of it, that way
        # relevant info can be updated between timesteps;

        # TODO:  where is FarmerAges used?
        FarmerAges = ppf.AgentAges(self.agent_domain, self.agent_array, self.Ny, self.Nx)

    def update(self):
        """Update agent variables.

        :return:

        """

        # Update self.agent_array
        # where in the model does the code denote that the agent goes from farmer to urban or visa versa
             # agent_domain[i][j].SwapAgent('aFarmer','aUrban',fromIndex,AgentArray) "switch for now"

        for i in np.arange(self.Ny):

            for j in np.arange(self.Nx):

                if self.agent_array[i][j]=='aFarmer':

                    self.agent_domain[i][j].FarmAgents[0].UpdateAge()

                    # TODO:  are you overwriting the previous value?
                    self.agent_domain[i][j].FarmAgents[0].UpdateDist2city(self.dist2city[i][j])

    def save_output(self):
        """Save output


        """
        pass

        # write landcover to array - sub w Jons work
        # saveLC(temp_lc, 2010, it, DataPath)


if __name__ == '__main__':

    Abm('/Users/d3y010/repos/github/IM3-BoiseState/example/config.yml')