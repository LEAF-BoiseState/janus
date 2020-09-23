"""
Created on Wed Aug 14 15:52:44 2019

@author: kendrakaiser
"""

import json
import unittest
import janus.agents.farmer as f


class AgentTest(unittest.TestCase):

    def test_eq(self):
        x = f.Farmer()
        y = f.Farmer()
        self.assertTrue(x == y)
        y = f.Farmer(Age=1)
        self.assertFalse(x == y)

    def test_farmerEncodeRoundtrip(self):
        x = f.Farmer(Age=1, Dist2city=2.0, LandStatus="unknown", nFields=1, alpha=0.24, beta=4.0)
        s = x.encode()
        y = f.Farmer()
        y = f.decode(s)
        self.assertEqual(x, y)

if __name__ == '__main__':
    unittest.main()
