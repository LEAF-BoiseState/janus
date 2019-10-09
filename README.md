[![Build Status](https://travis-ci.org/LEAF-BoiseState/janus.svg?branch=master)](https://travis-ci.org/LEAF-BoiseState/janus)

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

## Setting up a run

### Setup the `config.yml` file
There is an example config file in the `abm/example` directory of this package that describes each input.

| key | description |
| -- | -- |
| `f_counties_shp` | full path with file name and extension to the counties shapefile |
| `f_key_file` | full path with file name and extension to the land class category key file |
| `f_gcam_file` | GCAM raster file |
| `f_profits_file` | Profits file |
| `nt` | Number of timesteps |
| `switch_params` | list of lists for switching averse, tolerant parameters (alpha, beta) |
| `p` | proportion of each switching type, lower than p is averse, higher is tolerant |
| `fmin` | Need description |
| `fmax` | Need description |
| `f0` | Need description |
| `n` | Need description |
| `crop_seed_size` | Seed to set for random number generators for unit testing |
| `target_yr` | Initialization year assocciated with landcover input |
| `scale` | Scale of landcover grid in meters. Current options are 1000 and 3000 m |
| `county_list` | List of counties to evaluate |
| `agent_variables` | NASS variables to characterize agents with. Currently set to use "TENURE" and "AREA OPERATED" |
| `nass_year` | Year that NASS data are pulled from. This data is collected every 5 years, with the inital year here being 2007 |
| `nass_county_list` | List of counties in the domain that NASS data is collected from, these have to be capatalized |
| `nass_api_key` | A NASS API is needed to access the NASS data, get yours here https://quickstats.nass.usda.gov/api |

### Setup the input files
<Use this section to describe any processing needed to prepare input files for use.

- `file_one.csv`:  Need description
- `file_two.csv`:  Need description

## Running `janus`

### Running from terminal or command line
Ensure that you are using the desired `python` instance then run:

`python <path-to-abm-module>/model.py <path-to-the-config-file>`

### Running from a Python Prompt or from another script

```python
from janus import Janus
Janus('<path-to-config-file>')
```

## Outputs
<Use this section to describe the outputs>

- `output_one.csv`:  Need description
- `output_two.csv`:  Need description

## Community involvement
`janus` was built to be extensible.  It is our hope that the community will continue the development of this software.  Please submit a pull request for any work that you would like have considered as a core part of this package.  You will be properly credited for your work and it will be distributed under our current open-source license.  Any issues should be submitted through standard GitHub issue protocol and we will deal with these promptly.
