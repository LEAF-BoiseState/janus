import numpy as np
import pandas as pd
import geopandas as gpd
import yaml

import janus.crop_functions.crop_decider as crpdec


class ConfigReader:

    # keys found in the configuration file
    F_INIT_LC_FILE = 'f_init_lc_file'
    PROFITS = 'profits'
    F_PROFITS_FILE = 'f_profits_file'
    F_GCAM_PROFITS_FILE = 'f_gcam_profits_file'
    CAT_OPTION = 'cat_option'
    NT = 'nt'
    SWITCH_PARAMS = 'switch_params'
    P = 'p'
    FMIN = 'fmin'
    FMAX = 'fmax'
    N = 'n'
    CROP_SEED_SIZE = 'crop_seed_size'
    TARGET_YR = 'initialization_yr'
    SCALE = 'scale'
    AGENT_VARS = 'agent_variables'
    NASS_YR = 'nass_year'
    STATE = 'state'
    NASS_COUNTY_LIST = 'nass_county_list'
    NASS_API_KEY = 'nass_api_key'
    OUTPUT_DIR = 'output_directory'
    NETWORK_TYPE = 'network'
    DECISION_TYPE = 'decision_type'

    # county field name in the input shapefile
    COUNTY_FLD = 'county'

    def __init__(self, config_file):

        c = self.read_yaml(config_file)

        self.f_init_lc_file = c[ConfigReader.F_INIT_LC_FILE]

        self.profits = c[ConfigReader.PROFITS]

        self.profits_file = pd.read_csv(c[ConfigReader.F_PROFITS_FILE], header=None)

        self.gcam_profits_file = pd.read_csv(c[ConfigReader.F_GCAM_PROFITS_FILE], header=0)

        self.output_dir = c[ConfigReader.OUTPUT_DIR]

        self.cat_option = c[ConfigReader.CAT_OPTION]

        self.Nt = c[ConfigReader.NT]

        self.network = c[ConfigReader.NETWORK_TYPE]

        self.decision_type = c[ConfigReader.DECISION_TYPE]

        # set agent switching parameters (alpha, beta) [[switching averse], [switching tolerant]]
        self.switch = np.array(c[ConfigReader.SWITCH_PARAMS])

        # proportion of each switching type, lower than p is averse, higher is tolerant
        self.p = c[ConfigReader.P]

        # fraction of current profit at which the CDF is zero and one, and number of points to generate
        self.fmin = c[ConfigReader.FMIN]
        self.fmax = c[ConfigReader.FMAX]
        self.n = c[ConfigReader.N]

        # TODO:  define seed for crop decider; This is not used in this script but is set as `global`
        crpdec.define_seed(c[ConfigReader.CROP_SEED_SIZE])

        # target year
        self.target_year = c[ConfigReader.TARGET_YR]

        # scale of grid in meters
        self.scale = c[ConfigReader.SCALE]

        # agent variables
        self.agent_variables = c[ConfigReader.AGENT_VARS]

        # NASS year
        self.nass_year = c[ConfigReader.NASS_YR]

        # NASS state
        self.state = c[ConfigReader.STATE]

        # NASS county list
        self.nass_county_list = [i.upper() for i in c[ConfigReader.NASS_COUNTY_LIST]]

        # NASS API key
        self.nass_api_key = c[ConfigReader.NASS_API_KEY]

    @staticmethod
    def read_yaml(config_file):
        """Read the YAML config file to a dictionary.

        :param config_file:             Full path with file name and extension to the input config file.

        :return:                        YAML dictionary-like object

        """

        with open(config_file) as f:
            return yaml.safe_load(f)
