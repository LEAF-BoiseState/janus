"""
Agent Based Model of Land Use and Land Cover Change 

@author: Kendra Kaiser & Lejo Flores

@license: BSD 2-Clause
"""

import argparse
import os

import netCDF4 as netcdf
import numpy as np
import gdal, osr

import janus.preprocessing.geofxns as gf
import janus.crop_functions.crop_decider as crpdec
import janus.initialize_agents_domain as init_agent
import janus.postprocessing.create_figures as ppf
import janus.preprocessing.get_nass_agent_data as get_nass

from janus.config_reader import ConfigReader

class Janus:

    def __init__(self, config_file=None, args=None, save_result=True, plot_results=True):

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
        self.crop_ids, self.crop_id_all, self.ag, self.num_crops = self.initialize_crops()

        # initialize profits
        self.profits_actual, self.profit_signals = self.initialize_profit()

        # initialize agents
        self.agent_domain, self.agent_array = self.initialize_agents()

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

        ny, nx = lc.shape

        # initialize minimum distance to city
        dist2city = gf.min_dist_city(lc)

        domain = init_agent.initialize_domain(ny, nx)

        return lc, dist2city, domain, ny, nx

    def initialize_crops(self):
        """Initialize crops

        :return:    [0] numpy array; crop IDs that are in the domain
                    [1] numpy array; crop_id_all, land cover categories through time
                    [2] numpy array; ag, identifies where agricultural cells exist in the domain
                    [3] integer; num_crops, number of crops being assessed

        """

        ag = np.where(self.c.key_file['local_cat'] == 'ag')

        crop_ids_load = np.int64(self.c.key_file['local_GCAM_id_list'][ag[0]])

        num_crops = len(crop_ids_load)

        crop_ids = crop_ids_load.reshape(num_crops, 1)

        crop_id_all = np.zeros((self.c.Nt, self.Ny, self.Nx))

        crop_id_all[0, :, :] = self.lc

        return crop_ids, crop_id_all, ag, num_crops

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

        profits_actual = init_agent.init_profits(profit_signals, self.c.Nt, self.Ny, self.Nx, self.crop_id_all, self.crop_ids)

        return profits_actual, profit_signals

    def initialize_agents(self, cat_option='local'):
        """Initialize agents based on NASS data and initial land cover

        :param cat_option:      Denotes which categorization option is used, 'GCAM', 'local', or user defined
        :type cat_option:       String

        :return agent domain:   [0] Numpy array; agent_domain, domain with agent cell classes filled with agent info
                                [1] Numpy array; agent_array, strings that define which agent is in each location
        """

        tenure = get_nass.tenure_area(self.c.state, self.c.nass_county_list, self.c.nass_year, self.c.agent_variables,
                                      self.c.nass_api_key)

        ages = get_nass.ages(self.c.nass_year, self.c.state, self.c.nass_api_key)

        age_cdf = get_nass.make_age_cdf(ages)

        tenure_cdf = get_nass.make_tenure_cdf(tenure)

        agent_array = init_agent.place_agents(self.Ny, self.Nx, self.lc, self.c.key_file, cat_option)

        agent_domain = init_agent.agents(agent_array, self.domain, self.dist2city, tenure_cdf, age_cdf, self.c.switch,
                                         self.Ny, self.Nx, self.lc, self.c.attr, self.c.p)

        return agent_domain, agent_array

    def decisions(self):
        """Decision process.

        :return:    Updated domain with agent information and land cover choice
        :type:      Numpy Array

        """
        for i in np.arange(1, self.c.Nt):

            for j in np.arange(self.Ny):

                for k in np.arange(self.Nx):

                    if self.agent_domain[j, k].FarmerAgents:

                        # assess profit
                        profit_last, profit_pred = crpdec.assess_profit(self.crop_id_all[i-1, j, k],
                                                                       self.profits_actual[i-1, j, k],
                                                                       self.profit_signals[:, i],
                                                                       self.num_crops,
                                                                       self.crop_ids)

                        # identify the most profitable crop
                        crop_choice, profit_choice = crpdec.profit_maximizer(self.agent_domain[j, k].FarmerAgents[0].alpha,
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
                                                                                                    seed = False)

                        # update agent attributes
                        self.agent_domain[j, k].FarmerAgents[0].update_age()
                        if self.c.attr:
                            if self.agent_domain[j, k].FarmerAgents[0].LandStatus != 2:
                                self.agent_domain[j, k].FarmerAgents[0].update_switch()

    def plot_results(self):
        """Create result plots and save them."""

        ppf.plot_crop_percent(self.crop_id_all, self.crop_ids, self.c.Nt, self.num_crops, self.c.scale,
                              self.c.output_dir, self.c.key_file, self.ag)

        ppf.plot_agent_ages(self.agent_domain, self.agent_array, self.Ny, self.Nx, self.c.Nt, 
                            self.c.scale, self.c.output_dir)

        ppf.plot_switching_curves(self.agent_domain, self.agent_array, self.c.fmin, self.c.fmax, self.Ny, self.Nx,
                                  self.c.Nt, self.c.n, self.c.scale, self.c.output_dir,
                                  self.profits_actual[self.c.Nt-1, :, :], self.c.switch)

        ppf.plot_lc(self.crop_id_all, 0, self.c.target_year, self.c.output_dir, self.ag, self.crop_ids, self.num_crops, self.c.Nt, self.c.key_file)

        ppf.plot_lc(self.crop_id_all, 1, self.c.target_year, self.c.output_dir, self.ag, self.crop_ids, self.num_crops, self.c.Nt, self.c.key_file)
        ppf.plot_lc(self.crop_id_all, 29, self.c.target_year, self.c.output_dir, self.ag, self.crop_ids, self.num_crops, self.c.Nt, self.c.key_file)

        ppf.plot_price_signals(self.profit_signals, self.c.key_file, self.c.target_year, self.c.Nt, self.c.output_dir, self.c.profits)


    def save_outputs(self):
        """Save outputs as a netcdf file.

        The initial conditions are prepended to the output and all grids have
        the dimenstions Nt, Ny, Nx.
        """

        out_file = self.c.output_file
        years = [self.c.target_year + n for n in range(self.c.Nt)]

        # TODO(kyle): handle appending/assumed restart
        nc = netcdf.Dataset(out_file, 'w', format='NETCDF4')

        # Grab metadata from the original landcover file for geo referencing
        lc = gdal.Open(self.c.f_init_lc_file)
        gt = lc.GetGeoTransform()
        # GetProjectionRef() is safe for GDAL 2.x and 3.x, use GetSpatialRef() +
        # export as needed for GDAL 3.0+.
        srs = lc.GetProjectionRef()
        lc = None

        # set gdal based crs
        sr = nc.createVariable('spatial_ref', 'i4')
        sr.spatial_ref = srs

        # store number of pixel/lines in a more convenient variable
        # TODO(kyle): check axis ordering
        nx =  self.crop_id_all.shape[0]
        ny =  self.crop_id_all.shape[1]

        # setup the dimensions for the output file.
        # TODO(kyle): check on axis ordering
        # time is unlimited for appending
        dt = nc.createDimension('time', None)
        dx = nc.createDimension('x', nx)
        dy = nc.createDimension('y', ny)

        time = nc.createVariable('time', 'u2', ('time',))
        time.units = 'years'
        time.long_name = 'time'
        time[:] = years[:]

        # TODO(kyle): more axis ordering (-dy, dy, etc.), as well as half pixel
        # offsets.
        x = nc.createVariable('x', 'f8', ('x',))
        x.long_name = 'x coordinate'
        x[:] = [gt[0] + (0.5 * gt[1]) +  i * gt[1] for i in range(nx)]
        y = nc.createVariable('y', 'f8', ('y',))
        y.long_name = 'y coordinate'
        y[:] = [gt[3] + (0.5 * gt[5]) + i * gt[5] for i in range(ny)]

        lon = nc.createVariable('lon', 'f8', ('y', 'x'))
        lon.long_name = 'longitude'
        lon.units = 'degrees'
        lat = nc.createVariable('lat', 'f8', ('y', 'x'))
        lat.long_name = 'latitude'
        lat.units = 'degrees'

        # TODO(kyle): discuss how to handle errors.  If ImportFromWkt fails,
        # should we write the netcdf file without the geo-referencing?  For
        # now, just let gdal raise an exception.
        gdal.UseExceptions()
        s_srs = osr.SpatialReference()
        s_srs.ImportFromWkt(srs)
        t_srs = osr.SpatialReference()
        t_srs.ImportFromEPSG(4326)
        if gdal.VersionInfo() >= '3000000':
            t_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

        ct = osr.CoordinateTransformation(s_srs, t_srs)
        for i in range(ny):
            for j in range(nx):
                #TODO(kyle): do we need 1/2 pixel offsets?
                y = gt[3] + (0.5 * gt[5]) + i * gt[5]
                x = gt[0] + (0.5 * gt[1]) + j * gt[1]
                lon[i, j], lat[i, j], z = ct.TransformPoint(x, y)

        # TODO(kyle): check on range of crop values, cursory inspection showed
        # a max of 254, but it could have been the wrong file.
        crop = nc.createVariable('crop', 'i2', ('time', 'y', 'x'))
        crop.units = 'gcam(?) crop classification'
        crop.long_name = 'crop landcover'
        # prepend the initial conditions
        crop[:] = np.insert(self.crop_id_all, 0, self.lc, axis=0)
        crop.grid_mapping = 'spatial_ref'

        profits = nc.createVariable('profits', 'f8', ('time', 'y', 'x'))
        profits.units = 'total dollars (per unit area?)'
        profits.long_name = 'profit'
        # prepend zeros for the initial crop conditions
        profits[:] = np.insert(self.profits_actual, 0, np.zeros(self.lc.shape), axis=0)
        profits.grid_mapping = 'spatial_ref'

        # TODO(kyle): write the domain data

        nc.close()
        # This is a broader issue, discussion needed.
        gdal.DontUseExceptions()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config_file', type=str, help='Full path with file name and extension to YAML configuration file.')
    parser.add_argument('-s', '--switch_params', type=list, help='List of lists for switching averse, tolerant, and neutral parameters (alpha, beta)')
    parser.add_argument('-nt', '--nt', type=int, help='Number of time steps')
    parser.add_argument('-attr', '--attr', type=str, help='Boolean that determines if switching parameters are based on attributes')
    parser.add_argument('-f_init_lc', '--f_init_lc')

    # TODO: number of crops is calculated after doing the GIS pre-processing, if nc is needed for price generation, we might need to adjust this
    parser.add_argument('-nc', '--nc', type=int, help='Number of crops')
    parser.add_argument('-fmin', '--fmin', type=float, help='The fraction of current profit at which the CDF of the beta distribution is zero')
    parser.add_argument('-fmax', '--fmax', type=float, help='The fraction of current profit at which the CDF of the beta distribution is one')
    parser.add_argument('-n', '--n', type=int, help='The number of points to generate in the CDF')
    parser.add_argument('-seed', '--crop_seed_size', type=int, help='Seed to set for random number generators for unit testing')
    parser.add_argument('-yr', '--initialization_yr', type=int, help='Initialization year assocciated with landcover input')
    parser.add_argument('-state', '--state', type=str, help='State where NASS data is pulled from, capitalized acronym')
    parser.add_argument('-sc', '--scale', type=int, help='Scale of landcover grid in meters. Current options are 1000 and 3000 m')

    parser.add_argument('-av', '--agent_variables', type=list, help='NASS variables to characterize agents with. Currently set to use "TENURE" and "AREA OPERATED"')
    parser.add_argument('-nyr', '--nass_year', type=int, help='Year that NASS data are pulled from. This data is collected every 5 years, with the inital year here being 2007')
    parser.add_argument('-ncy', '--nass_county_list', type=list, help='List of counties in the domain that NASS data is collected from, these have to be entirely capatalized')
    parser.add_argument('-api', '--nass_api_key', type=int, help='A NASS API is needed to access the NASS data, get yours here https://quickstats.nass.usda.gov/api')

    args = parser.parse_args()

    Janus(args=args)
