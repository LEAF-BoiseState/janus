#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 22:15:11 2019

@author: kek25

function to create pdfs from NASS Data
"""
import nass
api = nass.NassApi("B5240598-2A7D-38EE-BF8D-816A27BEF504")
api.param_values('class_desc')

q = api.query()
age_cat=( "AGE LT 25", "AGE 25 TO 34", "AGE 35 TO 44", "AGE 45 TO 54", "AGE 55 TO 64", "AGE 65 TO 74", "AGE GE 75")
q.filter('commodity_desc', 'OPERATORS').filter('state_alpha', 'ID').filter('year', 2007).filter('class_desc', age_cat)
q.count()
ages=q.execute()

#2002, 2007, 2012...
def getNASSdata(countyList, year):
     #age
     #farm sizes
     #number of farms
     #number of principal operators
     #percentage of each tenure type
     
     
def getCropProduction(year):    
     #yeild, price, acres for each crop CDL to GCAM