[![Build Status](https://travis-ci.org/LEAF-BoiseState/janus.svg?branch=master)](https://travis-ci.org/LEAF-BoiseState/janus)

[![DOI](https://zenodo.org/badge/157612222.svg)](https://zenodo.org/badge/latestdoi/157612222)


# janus

`janus` was designed to simulate land cover changes over time. These landcover changes are carried out by individual agents that choose to either continue planting the same crop, or choose to switch to a new crop based on expected profits.

## Contact
- Kendra Kaiser (kendrakaiser@boisestate.edu)
- Lejo Flores (lejoflores@boisestate.edu)

## Getting Started
The `janus` package uses only Python 3.3 and up.

### Step 1:
Clone the repository into your desired directory:

`git clone https://github.com/LEAF-BoiseState/janus.git`

### Step 2:
You can install `janus` by running the following from your cloned directory (NOTE: ensure that you are using the desired `python` instance):

`python setup.py install`

### Step 3:
Confirm that the module and its dependencies have been installed by running from your prompt:

```python
from janus import Janus
```

If no error is returned then you are ready to go!

### Step 4:
If you choose to install the example data run the following (you must have write access to the directory you choose to store the data in):

```python
from janus import InstallSupplement

InstallSupplement(<directory you wish to install the data to>)
```

## Setting up a run

### Setup the `config.yml` file
There is an example config file in the `janus/example` directory of this package that describes each input.  To conduct a test run, install the data supplement as described above and replace the paths in the example config file with the location of where you installed the example data.  See the description below to match the example data file name with what is included with the package.

| Key | Description | Example Data Name
| -- | -- | -- |
| `f_counties_shp` | full path with file name and extension to the counties shapefile | `shp/counties_srb.shp` |
| `f_key_file` | full path with file name and extension to the land class category key file | `data/CDL2GCAM_categories.csv` |
| `f_gcam_file` | GCAM raster file | `data/gcam_2010_domain_3000.tiff` |
| `f_profits_file` | Profits file | `data/GenerateSyntheticPrices_test_output.csv` |
| `nt` | Number of timesteps | |
| `switch_params` | list of lists for switching averse, tolerant parameters (alpha, beta) | |
| `p` | Proportion of each switching type, lower than p is averse, higher is tolerant | |
| `fmin` | The fraction of current profit at which the CDF of the beta distribution is zero | |
| `fmax` | The fraction of current profit at which the CDF of the beta distribution is one | |
| `n` | The number of points to generate in the CDF | |
| `crop_seed_size` | Seed to set for random number generators for unit testing | |
| `target_yr` | Initialization year associated with landcover input | |
| `scale` | Scale of landcover grid in meters. Current options are 1000 and 3000 m | |
| `county_list` | List of counties to evaluate | |
| `agent_variables` | NASS variables to characterize agents with. Currently set to use "TENURE" and "AREA OPERATED" | |
| `nass_year` | Year that NASS data are pulled from. This data is collected every 5 years, with the Initialization year here being 2007 | |
| `nass_county_list` | List of counties in the domain that NASS data is collected from, these have to be capitalized | |
| `nass_api_key` | A NASS API is needed to access the NASS data, get yours here https://quickstats.nass.usda.gov/api | |

### Setup the input files

- `counties_shp.shp`:  Shapefile of counties within the area of interest. This should have county names and a single identifier for each polygon.

- `cdl.txt`:  Cropland Data Layer

- `key_file.csv`:  This file must have the following column titles 'CDL_id',	'CDL_name',	'GCAM_id',	'local_GCAM_id', 'GCAM_id_list',	'GCAM_name',	'GCAM_cat',	'local_GCAM_id_list',	'local_GCAM_name',	'local_cat'.

	'GCAM_id' and	'local_GCAM_id' are the conversion columns where the destination id is matched with each original CDL id.

	CDL_id, CDL_name, GCAM_id and GCAM_name are set based on the original CDL data and GCAM categorization.

	'id_list' are numeric identifiers for each category associated with names ('GCAM_name', 'local_GCAM_name') of output categorization.

	Columns that start with 'local' are where the file can be modified to create location specific landcover categories.

	'cat' is the generic category for assigning agents.'ag' for agricultural, 'nat' for natural (e.g. water, wetland), or 'urb' for urban land covers.

- `profits_file.csv`:  csv with the number of rows equal to number of crops. This contains the crop name, crop ID number, price function of choice and parameters for that function.


## Running `janus`

### Running from terminal or command line
Ensure that you are using the desired `python` instance then run:

`python <path-to-janus-module>/model.py --config_file <path-to-the-config-file>`

All parameters can be passed to the `Janus` class using terminal or command line instead of by a configuration file if you so desire.  Simply exclude the `config_file` argument from the required parameters. Run the following for assistance:

`python <path-to-janus-module>/model.py --help`

### Running from a Python Prompt or from another script

```python
from janus import Janus
Janus('<path-to-config-file>')
```

## Outputs

- `landcover.npy`:  Numpy array of landcover through time [Nt, Ny, Nx]
- `domain.npy`:  Numpy array of class type dcell that contain information about agents [Nt, Ny, Nx]
- `profits.npy`:  Numpy array of profits through time [Nt, Ny, Nx]


## Community involvement
`janus` was built to be extensible.  It is our hope that the community will continue the development of this software.  Please submit a pull request for any work that you would like have considered as a core part of this package.  You will be properly credited for your work and it will be distributed under our current open-source license.  Any issues should be submitted through standard GitHub issue protocol and we will deal with these promptly.
