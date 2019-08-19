#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:52:44 2019

@author: kendrakaiser
"""

import unittest
import numpy as np
import CropDecider as cd

class CropDeciderTest(unittest.TestCase):

    def test_switchingProbCurve(self):
        alpha=2
        beta=2
        fmin=0
        fmax=10
        n=5
        profit=1000
        
        x_known= np.array([0,2500,5000,7500,10000])
        f_known= np.array([0, 0.15625, 0.5, 0.84375, 1])
        
        x_test, f_test = cd.SwitchingProbCurve(alpha,beta,fmin,fmax,n,profit)
        
        self.assertEqual(x_known.all(), x_test.all())
        self.assertEqual(f_known.all(), f_test.all())
        
    def test_decide(self):
        
        alpha=2
        beta=2
        fmin=0
        fmax=10
        n=5
        profit=1000
        profit_p=1050
        
        ans = 0
        ans_test = cd.Decide(alpha,beta,fmin,fmax,n,profit,profit_p)
        
        self.assertEqual(ans, ans_test)
        
if __name__ == '__main__':
    unittest.main()