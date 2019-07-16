#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 18:33:36 2019

@author: lejoflores
"""

class Crop:
    def __init__(self, CropID, Name="none", PreHarvestEnergyCosts, 
        PreHarvestLaborCosts, PreHarvestMaterialCosts, HarvestEnergyCosts, 
        HarvestLaborCosts, HarvestMaterialCosts, CropPrice, AreaCultivated):
        
        self.CropID = CropID
        self.CropYield = CropYield
        self.CropPrice = CropPrice

        self.PreHarvestEnergyCosts = PreHarvestEnergyCosts
        self.PreHarvestLaborCosts = PreHarvestLaborCosts
        self.PreHarvestMaterialCosts = PreHarvestMaterialCosts
        self.PreHarvestCosts = PreHarvestEnergyCosts + PreHarvestLaborCosts + PreHarvestMaterialCosts
        
        self.HarvestEnergyCosts = HarvestEnergyCosts
        self.HarvestLaborCosts = HarvestLaborCosts
        self.HarvestMaterialCosts = HarvestMaterialCosts
        self.HarvestCosts = HarvestEnergyCosts + HarvestLaborCosts + HarvestMaterialCosts
        
        self.Costs = self.PreHarvestCosts + self.HarvestCosts # Cost per unit area of this crop
        self.TotalCosts = self.AreaCultivated * self.Costs
