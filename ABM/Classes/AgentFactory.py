#!/usr/bin/env python3

from aUrban import aUrban
from aFarmer import aFarmer

class AgentFactory(object):

    # declare constant variables
    _CONST_AGENT_COLUMN_INDEX = {
        "aUrban" : 0,
        "aFarmer" : 1
    }

    @staticmethod
    def CreateAgent(type):
        if type == 'aUrban' : return aUrban()
        if type == 'aFarmer' : return aFarmer()
        assert 0, "Invalid Agent Type: " + type

    @staticmethod
    def IsAgentTypeValid(type):
        return type == 'aUrban' or type == "aFarmer"

    @staticmethod
    def AgentTypeCount():
        return 2

    @staticmethod
    def GetColumnIndex(self, type):
        if self.isAgentTypeValid(type) is False: raise Exception("Invalid Agent Type: " + type)
        return self._CONST_AGENT_COLUMN_INDEX[type]
