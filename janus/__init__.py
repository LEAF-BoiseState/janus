from janus.model import *
from janus.install_supplement import *
from janus.preprocessing.get_gis_data import get_gis_data

__all__ = ['Janus', 'InstallSupplement', 'get_gis_data']



import janus

# prepare GIS data
janus.get_gis_data()

# run model
...


