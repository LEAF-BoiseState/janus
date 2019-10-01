# abm

`abm` was designed to simulate land cover changes over time. These landcover changes are carried out by individual agents that choose to either continue planting the same crop, or choose to switch to a new crop based on expected profits.

## Contact
- Kendra Kaiser (kendrakaiser@boisestate.edu)
- Lejo Flores (lejoflores@boisestate.edu)

## Getting Started
The `abm` package uses only Python 3.3 and up.

### Step 1:
Clone the repository into your desired directory:

`git clone https://github.com/LEAF-BoiseState/IM3-BoiseState.git`

### Step 2:
You can install `abm` by running the following from your cloned directory (NOTE: ensure that you are using the desired `python` instance):

`python setup.py install`

### Step 3:
Confirm that the module and its dependencies have been installed by running from your prompt:

```python
from abm import Abm
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
| `nt` | Need description |
| `nc` | Need description |
| `switch_params` | list of lists for switching averse, tolerant parameters (alpha, beta) |
| `p` | proportion of each switching type, lower than p is averse, higher is tolerant |
| `fmin` | Need description |
| `fmax` | Need description |
| `f0` | Need description |
| `n` | Need description |
| `crop_seed_size` | Need description |
| `target_yr` | Need description |
| `scale` | Need description |
| `county_list` | List of counties to evaluate |
| `agent_variables` | Need description |
| `nass_year` | Need description |
| `nass_county_list` | Need description |
| `nass_api_key` | Need description |

### Setup the input files
<Use this section to describe any processing needed to prepare input files for use.

- `file_one.csv`:  Need description
- `file_two.csv`:  Need description

## Running `abm`

### Running from terminal or command line
Ensure that you are using the desired `python` instance then run:

`python <path-to-abm-module>/model.py <path-to-the-config-file>`

### Running from a Python Prompt or from another script

```python
from abm import Abm
Abm('<path-to-config-file>')
```

## Outputs
<Use this section to describe the outputs>

- `output_one.csv`:  Need description
- `output_two.csv`:  Need description

## Community involvement
`abm` was built to be extensible.  It is our hope that the community will continue the development of this software.  Please submit a pull request for any work that you would like have considered as a core part of this package.  You will be properly credited for your work and it will be distributed under our current open-source license.  Any issues should be submitted through standard GitHub issue protocol and we will deal with these promptly.
