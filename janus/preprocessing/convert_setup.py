"""
Created on Sun Nov 22, 2019

@author: Kendra Kaiser

Setup input files to convert prices from GCAM-USA into a format that is readable by Janus (22 rows and nt columns)
"""

CropFileIn ='/Users/kek25/Desktop/Data/output_SRB_Reference_Perfect.csv'
CropFileOut = '/Users/kek25/Desktop/Data/GCAMvalues.csv'
year = 2010
key_file = '/Users/kek25/Desktop/Data/CDL2GCAM_categories.csv'
res = 3
nc = 19
nt = 30
results_path = '/Users/kek25/Desktop/Data/Results/'