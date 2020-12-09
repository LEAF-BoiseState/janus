"""
Created on Wed Nov 25 16:05 2020
@author: kendra kaiser
Ingests land cover percent files from janus output and creates pdfs of crops from each ensemble run
"""
import glob
import numpy as np
import pandas as pd
import seaborn as sb


#dir_name = '/Users/kendrakaiser/Desktop/Janus_run/smallworld/highswitch/*.csv'
#dir_name = '/Users/kendrakaiser/Desktop/Janus_run/profitmax/lowswitch/*.csv'
dir_name = '/Users/kendrakaiser/Desktop/Janus_run/erdosrenyi/highswitch_ed01/*.csv'

files = glob.glob(dir_name)
data = np.zeros((1, 20))
for fname in files:
    with open(fname, 'r') as f:
        dat = pd.read_csv(f)
        data = np.append(data, np.array(dat.iloc[:, -1]).reshape((1, len(dat))), axis=0)

data = data[1:, :]
data1 = data[:, ~np.all(data == 0, axis=0)]
# data = pd.DataFrame(np.nan_to_num(data))

p = sb.displot(data1, kind='kde')
p = (p.set_axis_labels("Agents","Percent"))
p.set(xlim=(0, 400))
p.savefig('/Users/kendrakaiser/Desktop/Janus_run/ed01.eps')
