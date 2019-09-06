#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 14:08:22 2019

@author: kendrakaiser
"""

import unittest
import getNASS_Agent_data as nass

class CropDeciderTest(unittest.TestCase):

    def test_cleanup(self):
        
        test_val=nass.cleanup('2,400')
        
        known_val=int(2400)
        
        self.assertEqual(test_val, known_val)


if __name__ == '__main__':
    unittest.main()
        