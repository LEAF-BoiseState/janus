"""
Created on Mon Apr  8 22:15:11 2019

@author: kek25

function to create pdfs from NASS Data
"""
import nass
import pandas as pd
import numpy as np


def cleanup(value):
    """Massage data into proper form.

    :param value:

    :return:

    """
    try:
        return int(value.replace(',', ''))

    except ValueError:
        return 0


def ages(YR, state, nass_api_key):
    """Need description.

    :param YR:
    :param state:
    :param nass_api_key:

    :return:

    """
    api = nass.NassApi(nass_api_key)

    q = api.query()

    # prepare lists for data
    age_cat = ["AGE LT 25", "AGE 25 TO 34", "AGE 35 TO 44", "AGE 45 TO 54", "AGE 55 TO 64", "AGE 65 TO 74", "AGE GE 75"]
    q.filter('commodity_desc', 'OPERATORS').filter('state_alpha', state).filter('year', YR).filter('class_desc', age_cat)
    age_dF = pd.DataFrame(q.execute())
    age_dF['Value'] = age_dF['Value'].apply(cleanup)
    
    ages = pd.DataFrame(0, index=np.arange(len(age_dF)), columns=('category', 'operators'))
    ages['category'] = age_cat.copy()
     
    for i in range(len(age_dF)):

        # state level aggregation
        vals = age_dF[(age_dF['class_desc'] == ages.loc[i, 'category'])]
        ages.loc[i, 'operators'] = int(vals['Value'])

    return ages


def tenure_area(state, county_list, NASS_yr, variables, nass_api_key):
    """County level aggregation, can change to report each county

    :param state:
    :param county_list:
    :param NASS_yr:
    :param variables:
    :param nass_api_key:

    :return:

    """
    api = nass.NassApi(nass_api_key)

    q = api.query()

    q.filter('commodity_desc', 'FARM OPERATIONS').filter('state_alpha', state).filter('year', NASS_yr).filter('domain_desc', variables).filter('county_name', county_list)
    data = q.execute()
    dataF = pd.DataFrame(data)
    dataF['Value'] = dataF['Value'].apply(cleanup)
    
    # prepare lists for data
    area_cat = ["AREA OPERATED: (1.0 TO 9.9 ACRES)","AREA OPERATED: (10.0 TO 49.9 ACRES)", "AREA OPERATED: (50.0 TO 69.9 ACRES)", "AREA OPERATED: (70.0 TO 99.9 ACRES)", "AREA OPERATED: (100 TO 139 ACRES)","AREA OPERATED: (140 TO 179 ACRES)", "AREA OPERATED: (180 TO 219 ACRES)", "AREA OPERATED: (220 TO 259 ACRES)", "AREA OPERATED: (260 TO 499 ACRES)", "AREA OPERATED: (500 TO 999 ACRES)", "AREA OPERATED: (1,000 TO 1,999 ACRES)", "AREA OPERATED: (2,000 OR MORE ACRES)"]#, "AREA OPERATED: (50 TO 179 ACRES)", "AREA OPERATED: (180 TO 499 ACRES)", "AREA OPERATED: (1,000 OR MORE ACRES)"]
    tenure_cat = ["TENURE: (FULL OWNER)", "TENURE: (PART OWNER)", "TENURE: (TENANT)" ]
    cat=tenure_cat + area_cat
    
    farms=pd.DataFrame(0, index=np.arange(len(cat)), columns=('category', 'acres', 'operations'))
    farms['category'] = cat
    
    for i in range(len(cat)):
        sub=dataF[(dataF['domaincat_desc'] == farms.loc[i,'category']) & (dataF['unit_desc'] == 'ACRES')]
        farms.loc[i, 'acres'] = sum(sub['Value']) # acres
        sub2=dataF[(dataF['domaincat_desc'] == farms['category'][i]) & (dataF['unit_desc'] == 'OPERATIONS')]

        # operations
        farms.loc[i, 'operations'] = sum(sub2['Value'])

    return farms


def make_age_cdf(var_array):
    """Create distributions from NASS data.

    :param var_array:

    :return:

    """
    
    ser_full = np.zeros(0)

    var_array['low'] =[18, 25, 35, 45, 55, 65, 75]
    var_array['high'] =[25, 35, 45, 55, 65, 75, 86]

    # create a full series of ages based on number in each category
    for i in np.arange(7):
        ser = np.random.randint(var_array.low[i], high=var_array.high[i], size=var_array.operators[i])
        ser_full = np.append(ser_full, ser)
        
    H, X1 = np.histogram(ser_full, bins=68, density=True)

    X2 = np.floor(X1)
    dx = X2[2] - X2[1]
    F1 = np.cumsum(H) * dx
    perc = np.column_stack((X2[1:], F1))
    
    return perc


def make_tenure_cdf(var_array):
    """

    :param var_array:

    :return:

    """

    ser_full = np.zeros(0)

    ser0 = np.zeros(var_array['operations'][0])
    ser1 = np.ones(var_array['operations'][1])
    ser2 = np.ones(var_array['operations'][2]) + 1
    ser_full = np.append(ser_full, ser0)
    ser_full = np.append(ser_full, ser1)
    ser_full = np.append(ser_full, ser2)
        
    H, X1 = np.histogram(ser_full, bins=3, density=True)
    dx = X1[2] - X1[1]
    F1 = np.cumsum(H) * dx # I think this is the one to return
    perc = np.column_stack(([0, 1, 2], F1))

    return perc
    

def farmer_data(TenureCDF, AgeCDF, switch, p, d2c):
    """Collect agent data from NASS distributions and place in dictionary.

    :param TenureCDF:
    :param AgeCDF:
    :param switch:
    :param p:
    :param d2c:

    :return:

    """
    ss=np.random.random_sample()
    ts = np.random.random_sample() 
    ageS = np.random.random_sample()

    if ss >= p:
        k= 0
    else:
        k =1
    
    if ageS < AgeCDF[0, 1]:
        ageI = 18
    else: 
        ageT = np.where(AgeCDF[:, [1]] <= ageS)
        ageI = max(ageT[0])
            
    tt = np.where(TenureCDF[:, [1]] >= ts)
    tenStat = min(tt[0])
    
    AgentData = {
            "AgeInit" : ageI,
            "LandStatus" : tenStat,
            "Alpha": switch[k][0],
            "Beta": switch[k][1],
            "nFields": 1,
            "Dist2city": d2c
                }
    return AgentData


def urban_data(lc):
    """Pull the landcover category from lc, set this so it's 0 =open space, 1=low, 2=med, 3=high density
    this needs to be set by user based on what their landcover classes are, e.g. denisty would not
    be a category with original GCAM cats

    :param lc:

    :return:

    """
    # TODO:  Need closing condition (else: ...)
    if lc == 17:
        d = 3
    elif lc == 25:
        d = 2
    elif lc == 26:
        d = 1
    elif lc == 27:
        d = 0

    agent_data = {"Density": d}

    return agent_data
