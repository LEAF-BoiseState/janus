# Author: Kendra Kaiser
# Date: 8/13/2019
# FileName: urban.py
# Purpose: Holds definition of urban agent


class Urban:
    """ Urban agents exist in locations where the land cover is urban, the class contains their attributes.
    The urban agent is currently not in use in Janus, but is a placeholder for future development.
    :param density:     Density of urban location, high medium or low
    :type density:      String
    """

    def __init__(self, **kwargs):
        
        self.density = kwargs.get('density')

        assert(self.density == 0 or self.density == 1 or self.density == 2)
