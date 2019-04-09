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
#pd.options.mode.chained_assignment = None
#api.param_values('class_desc')
#q.count()

api = nass.NassApi("B5240598-2A7D-38EE-BF8D-816A27BEF504")
q = api.query()

#prepare lists for data 
age_cat=["AGE LT 25", "AGE 25 TO 34", "AGE 35 TO 44", "AGE 45 TO 54", "AGE 55 TO 64", "AGE 65 TO 74", "AGE GE 75"]
area_cat=["AREA OPERATED: (1.0 TO 9.9 ACRES)","AREA OPERATED: (10.0 TO 49.9 ACRES)", "AREA OPERATED: (50.0 TO 69.9 ACRES)", "AREA OPERATED: (70.0 TO 99.9 ACRES)", "AREA OPERATED: (100 TO 139 ACRES)","AREA OPERATED: (140 TO 179 ACRES)", "AREA OPERATED: (180 TO 219 ACRES)", "AREA OPERATED: (220 TO 259 ACRES)", "AREA OPERATED: (260 TO 499 ACRES)", "AREA OPERATED: (500 TO 999 ACRES)", "AREA OPERATED: (1,000 TO 1,999 ACRES)", "AREA OPERATED: (2,000 OR MORE ACRES)"]#, "AREA OPERATED: (50 TO 179 ACRES)", "AREA OPERATED: (180 TO 499 ACRES)", "AREA OPERATED: (1,000 OR MORE ACRES)"]          
tenure_cat=["TENURE: (FULL OWNER)", "TENURE: (PART OWNER)", "TENURE: (TENANT)" ]  
cat=tenure_cat + area_cat


  
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
    ages=[0]*len(age_dat)
    for i in range(len(age_dat)):
        ages[i]=cleanup(age_dat[i]['Value'])
    return(ages)
    

variables=["TENURE", "AREA OPERATED"]
counties=['ADA', 'CANYON']
YR=2007
countyList='ADA'
countyList=counties


def getNASSdata(countyList, YR):
    q = api.query()
    q.filter('commodity_desc', 'FARM OPERATIONS').filter('state_alpha', 'ID').filter('year', YR).filter('domain_desc', variables).filter('county_name', countyList)
    data=q.execute()
    dataF=pd.DataFrame(data)
    dataF['Value']=dataF['Value'].apply(cleanup)    
    
    farms=pd.DataFrame(0, index=np.arange(len(cat)), columns=('category', 'acres', 'operations'))
    farms['category']= cat
    
    for i in range(len(cat)):
        sub=dataF[(dataF['domaincat_desc'] == farms['category'][i]) & (dataF['unit_desc'] == 'ACRES')]
        farms['acres'][i] = sub['Value']
        sub2=dataF[(dataF['domaincat_desc'] == farms['category'][i]) & (dataF['unit_desc'] == 'OPERATIONS')]
        farms['operations'][i] = sub2['Value']

    return(farms)





def getCropProduction(year):    
     #yeild, price, acres for each crop CDL to GCAM
     q=api.query()
     q.filter()

    
ages=getAges(2007)
tenure=getNASSdata('ADA', 2007)