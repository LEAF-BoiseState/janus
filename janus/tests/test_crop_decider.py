"""
Created on Wed Aug 14 15:52:44 2019

@author: kendrakaiser
"""

import unittest
import numpy as np
import janus.crop_functions.crop_decider as cd


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
        
        x_test, f_test = cd.switching_prob_curve(alpha,beta,fmin,fmax,n,profit)
        
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
        ans_test = cd.decide2switch(alpha,beta,fmin,fmax,n,profit,profit_p)
        
        self.assertEqual(ans, ans_test)
        
    def test_assessProfit(self):
        Crop = np.float64(15)
        Profits_cur =np.array([33335, 15559, 27343, 12477])
        Profits_alt = np.array([31114, 15964, 27966, 14310])
        Nc= 4
        CropIDs =np.array([1,2,3,10])
        
        Profit_ant_test, Profit_p_test = cd.assess_profit(Crop, Profits_cur, Profits_alt, Nc, CropIDs)
        
        Profit_ant_known=np.array([0])
        Profit_p_known=np.zeros([4,1])
        
        self.assertEqual(Profit_ant_test, Profit_ant_known)
        self.assertEqual(Profit_p_test.all(), Profit_p_known.all())
        
    def test_decideN(self):
        
        alpha=2
        beta=2
        fmin=0
        fmax=10
        n=5
        profit=1000
        vec_crops=np.array([1,2,3,10])
        vec_crops=vec_crops.reshape((4,1))
        vec_profit_p=np.zeros([4,1])
        
        CropChoice_test, ProfitChoice_test = cd.profit_maximizer(alpha, beta, fmin, fmax, n, profit, vec_crops, \
                                                      vec_profit_p, rule=True)
        
        CropChoice_known = -1
        ProfitChoice_known = -1
        
        self.assertEqual(CropChoice_test, CropChoice_known)
        self.assertEqual(ProfitChoice_test, ProfitChoice_known)
        
    def test_MakeChoice(self):
        cd.define_seed(5)
        
        CropID_all=np.float64(15)
        Profit_last=0
        CropChoice=-1
        ProfitChoice=-1
 
        CropID_all_known=np.float(15.0)
        Profit_act_known =np.array([[[441.22748689]]])
        
        CropID_all_test, Profit_act_test  = cd.make_choice(CropID_all, Profit_last, CropChoice, ProfitChoice, seed=True)
        
        self.assertEqual(CropID_all_known, CropID_all_test)
        self.assertEqual(Profit_act_known.astype('int'), Profit_act_test.astype('int'))


if __name__ == '__main__':
    unittest.main()
