"""
Created on Wed Nov 25 16:05 2020
@author: kendra kaiser
Ingests land cover percent files from janus output and creates pdfs of crops from each ensemble run
"""
import glob
import numpy as np
import pandas as pd
import seaborn as sb
dir = '/Users/kendrakaiser/Desktop/Janus_run/smallworld/lowswitch/*.csv'
#dir = '/Users/kendrakaiser/Desktop/Janus_run/profitmax/'
#dir = '/Users/kendrakaiser/Desktop/Janus_run/erdosrenyi/'

files = glob.glob(dir)
data = np.zeros((1, 20))
for fname in files:
    with open(fname, 'r') as f:
        dat = pd.read_csv(f)
        data = np.append(data, np.array(dat.iloc[:,-1]).reshape((1, len(dat))), axis=0)

data = data[1:, :]
data1 = data[:, ~np.all(np.isnan(data), axis=0)]
data = pd.DataFrame(np.nan_to_num(data))


g = sb.FacetGrid(data, col='columns')
g = (g.map(sb.distplot, 'value'))

data.plot.kde()

sb.displot(data1, kind='kde')