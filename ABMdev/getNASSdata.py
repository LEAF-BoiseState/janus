#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 22:15:11 2019

@author: kek25

function to create pdfs from NASS Data
"""
import nass
import pandas as pd
import numpy as np
#api.param_values('class_desc')
q.count()

api = nass.NassApi("B5240598-2A7D-38EE-BF8D-816A27BEF504")
q = api.query()
age_cat=["AGE LT 25", "AGE 25 TO 34", "AGE 35 TO 44", "AGE 45 TO 54", "AGE 55 TO 64", "AGE 65 TO 74", "AGE GE 75"]

def cleanup(value):
    ''' Massage data into proper form '''
    try:
        return int(value.replace(',', ''))
        # Some contain strings with '(D)'
    except ValueError:
        return 0

#Only 2007 and 2012?
def getAges(YR):
    q = api.query()
    q.filter('commodity_desc', 'OPERATORS').filter('state_alpha', 'ID').filter('year', YR).filter('class_desc', age_cat)
    age_dat=q.execute()
    ages=[0]*7
    for i in range(7):
        ages[i]=cleanup(age_dat[i]['Value'])
    return(ages)
    

variables=["TENURE", "AREA OPERATED"]
counties=['ADA', 'CANYON']

def getNASSdata(countyList, YR):
    q = api.query()
    q.filter('commodity_desc', 'FARM OPERATIONS').filter('state_alpha', 'ID').filter('year', 2007).filter('domain_desc', 'TENURE').filter('county_name', 'ADA')
    tenure_dat=q.execute()
    tenure=pd.DataFrame(0, index=np.arange(len(tenure_dat)), columns=('cat', 'acres'))
    for ix in range(len(tenure_dat)):
        for dic in tenure_dat:
           tempt=dic['domaincat_desc']
           tempv=cleanup(dic['Value'])
           
        tenure['cat'][ix]=tempt
        tenure['acres'][ix]=tempv
        
     #farm sizes
     #number of farms
     #number of principal operators
     #percentage of each tenure type
     
     
def getCropProduction(year):    
     #yeild, price, acres for each crop CDL to GCAM
     