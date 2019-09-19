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

   
def cleanup(value):
    ''' Massage data into proper form '''
    try:
        return int(value.replace(',', ''))
        # Some contain strings with '(D)'
    except ValueError:
        return 0

#Only 2007 and 2012 for the state
def Ages(YR,q):
    #prepare lists for data 
    age_cat=["AGE LT 25", "AGE 25 TO 34", "AGE 35 TO 44", "AGE 45 TO 54", "AGE 55 TO 64", "AGE 65 TO 74", "AGE GE 75"]
    api = nass.NassApi("B5240598-2A7D-38EE-BF8D-816A27BEF504")
    q = api.query()
    q.filter('commodity_desc', 'OPERATORS').filter('state_alpha', 'ID').filter('year', YR).filter('class_desc', age_cat)
    age_dF=pd.DataFrame(q.execute())
    age_dF['Value']=age_dF['Value'].apply(cleanup) 
    
    ages=pd.DataFrame(0, index=np.arange(len(age_dF)), columns=('category', 'operators'))
    ages['category']=age_cat.copy()
     
    for i in range(len(age_dF)):
        vals =age_dF[(age_dF['class_desc'] == ages.loc[i,'category'])] #state level aggregation
        ages.loc[i,'operators']=int(vals['Value'])
    return(ages)
    
def TenureArea(countyList, YR, variables): #countly level aggregation, can change to report each county ...
    
    api = nass.NassApi("B5240598-2A7D-38EE-BF8D-816A27BEF504")
    q = api.query()
    q.filter('commodity_desc', 'FARM OPERATIONS').filter('state_alpha', 'ID').filter('year', YR).filter('domain_desc', variables).filter('county_name', countyList)
    data=q.execute()
    dataF=pd.DataFrame(data)
    dataF['Value']=dataF['Value'].apply(cleanup)    
    
    #prepare lists for data 
    area_cat=["AREA OPERATED: (1.0 TO 9.9 ACRES)","AREA OPERATED: (10.0 TO 49.9 ACRES)", "AREA OPERATED: (50.0 TO 69.9 ACRES)", "AREA OPERATED: (70.0 TO 99.9 ACRES)", "AREA OPERATED: (100 TO 139 ACRES)","AREA OPERATED: (140 TO 179 ACRES)", "AREA OPERATED: (180 TO 219 ACRES)", "AREA OPERATED: (220 TO 259 ACRES)", "AREA OPERATED: (260 TO 499 ACRES)", "AREA OPERATED: (500 TO 999 ACRES)", "AREA OPERATED: (1,000 TO 1,999 ACRES)", "AREA OPERATED: (2,000 OR MORE ACRES)"]#, "AREA OPERATED: (50 TO 179 ACRES)", "AREA OPERATED: (180 TO 499 ACRES)", "AREA OPERATED: (1,000 OR MORE ACRES)"]          
    tenure_cat=["TENURE: (FULL OWNER)", "TENURE: (PART OWNER)", "TENURE: (TENANT)" ]  
    cat=tenure_cat + area_cat
    
    farms=pd.DataFrame(0, index=np.arange(len(cat)), columns=('category', 'acres', 'operations'))
    farms['category']= cat
    
    for i in range(len(cat)):
        sub=dataF[(dataF['domaincat_desc'] == farms.loc[i,'category']) & (dataF['unit_desc'] == 'ACRES')]
        farms.loc[i,'acres']= sum(sub['Value']) #acres
        sub2=dataF[(dataF['domaincat_desc'] == farms['category'][i]) & (dataF['unit_desc'] == 'OPERATIONS')]
        farms.loc[i,'operations'] =sum(sub2['Value']) #operations

    return(farms)
 
def makeAgeCDF(varArray):
    
    serFull=np.zeros(0)

    varArray['low'] =[18, 25, 35, 45, 55, 65, 75]
    varArray['high'] =[25, 35, 45, 55, 65, 75, 86]
        #create a full series of ages based on number in each category
    for i in np.arange(7):
        ser=np.random.randint(varArray.low[i], high =varArray.high[i], size = varArray.operators[i])
        serFull=np.append(serFull, ser)
        
    H,X1 = np.histogram(serFull, bins = 68, normed=True)
    X2=np.floor(X1)
    dx = X2[2] - X2[1]
    F1 = np.cumsum(H)*dx
    perc=np.column_stack((X2[1:],F1))
    perc
    
    return(perc)
 
def makeTenureCDF(varArray):
    serFull=np.zeros(0)
    

    ser0= np.zeros(varArray['operations'][0])
    ser1= np.ones(varArray['operations'][1])
    ser2= np.ones(varArray['operations'][2]) +1
    serFull=np.append(serFull, ser0)
    serFull=np.append(serFull, ser1)
    serFull=np.append(serFull, ser2)
        
    H,X1 = np.histogram(serFull, bins = 3, normed=True)
    dx = X1[2] - X1[1]
    F1 = np.cumsum(H)*dx #I think this is the one to return
    perc=np.column_stack(([0,1,2], F1))        
    return(perc)
    
#def setAgentParams - should move the param selection here and use it in the initAgent function