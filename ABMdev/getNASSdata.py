#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 22:15:11 2019

@author: kek25

function to create pdfs from NASS Data
"""
import nass
#api.param_values('class_desc')
#q.count()

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

#2007, 2012...
def getAges(YR):
    q.filter('commodity_desc', 'OPERATORS').filter('state_alpha', 'ID').filter('year', YR).filter('class_desc', age_cat)
    age_dat=q.execute()
    ages=[0]*7
    for i in range(7):
        ages[i]=cleanup(age_dat[i]['Value'])
    
    return(ages)
    
    

def getNASSdata(countyList, year):

     #farm sizes
     #number of farms
     #number of principal operators
     #percentage of each tenure type
     
     
def getCropProduction(year):    
     #yeild, price, acres for each crop CDL to GCAM
     