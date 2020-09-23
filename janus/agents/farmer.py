# Author: Jonathan Carvajal
# Date: 8/13/2019
# FileName: farmer.py
# Purpose: Holds definition of farmer

import json

class Farmer:
    """ The farmer class holds all relevant information about farmer agents. All attributes are optional.
    :param Age:         Age of agent
    :type Age:          Int
    :param Dist2city:   Distance from agents location to the nearest city cell
    :type Dist2city:    Float
    :param LandStatus:  Farmers ownership status, e.g. tenured, owner, part owner
    :type LandStatus:   String
    :param nFields:     Number of fields that the farmer is managing
    :type nFields:      Int
    :param alpha:       Alpha parameter for the incomplete beta distribution
    :type alpha:        Float
    :param beta:        Beta parameter for the incomplete beta distribution
    :type beta:         Float

    """
    def __init__(self, **kwargs):
        self.Age = kwargs.get('Age')
        self.Dist2city = kwargs.get('Dist2city')

        self.LandStatus = kwargs.get('LandStatus')
        self.nFields = kwargs.get('nFields')

        self.alpha = kwargs.get('alpha')
        self.beta = kwargs.get('beta')

    def __eq__(self, other):
        return self.Age == other.Age and \
            self.Dist2city == other.Dist2city and \
            self.LandStatus == other.LandStatus and \
            self.nFields == other.nFields and \
            self.alpha == other.alpha and \
            self.beta == other.beta

    def update_age(self):
        """ Updates the age of the agent by one year """
        self.Age += 1

    def update_dist2city(self, new_dist):
        """ Updates the distance of the farmer to the city given new land cover"""
        self.Dist2city = new_dist

    def update_switch(self):
        """ Updates the farmers likelihood of switching their crop such that they are less likely to switch as they age
         """
        self.alpha += 0.1
        self.beta -= 0.01

    def encode(self):
        return json.dumps(self.__dict__)

def decode(s):
    """ Override the values in self with parameters from the json representation of a Farmer"""
    d = json.loads(s)
    return Farmer(**d)
