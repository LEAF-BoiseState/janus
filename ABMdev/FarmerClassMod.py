## DEPRECATED

#=============================================================================#
#                                                                             #
#                           FarmerClassMod.py                                 #
#                                                                             #
# PURPOSE: The purpose of this file is to serve as a module in which we def-  #
#          ine the Farmer Object, its properties, and associated decision     #
#          rules.                                                             #
#                                                                             #
# AUTHOR: Lejo Flores                                                         #
#                                                                             #
# DATE: 1/29/2019                                                             #
#                                                                             #
# OBJECTIVES: Within this module and associated class definition, the follow- #
#             ing questions should be able to be answered:                    #
#                 1. What is a FarmerObject and what are its attributes?      #
#                    - Age [yr]: initialized in the constructor, but dynamic  #
#                    - Distance [km]: initialized in constructor, but dynamic #
#                    - On Farm Income [$]: initialized in constructor, but    #
#                      dynamic                                                #
#                    - Off Farm Income [$]: initialized in constructor, but   #
#                      dynamic                                                #
#                    - Crop id [-]: initialized in constructor, but dynamic.  #
#                      This is an integer index value that represents crop    #
#                      type.                                                  #
#                    The following attributes are potentially important, but  #
#                    not yet implemented:                                     #
#                    - Farm area [km^2]: area cultivated                      #
#                    - Irrigated: 0 - no; 1 - surface water, 2 - groundwater, #
#                      3 - surface and groundwater                            # 
#                    - Fraction irrigated [0-1]: fraction of farm irrigated   #
#                    - Julian priority date [0-366]: Priority date for        #
#                      surface water irrigation                               #
#                    - Surface water allocation [m^3/d]: Allocation flow rate #
#                      for surface water irrigation                           #
#                    - Groundwater allocation [m^3/d]: Allocation flow rate   #
#                      for groundwater                                        #
#                    - Irrigation type: 1 - Flood, 2 - Sprinkler, 3 - Drip,   #
#                      4 - Mixed                                              #
#                 2. What can/does a FarmerObject do?                         #
#                    - Gets older                                             #
#                    - Gets potentially encroached by an urban "bubble"       #
#                    - Has on farm income imposed externally by crop prices   #
#                    - Has off farm income imposed externally                 #
#                    The following are actions not yet implemented:           #
#                    - Considers alternative crop choices based on inferred   #
#                      difference in average on-farm income                   #
#                    - Considers alternative crop choices based on inffered   #
#                      difference in variance in on-farm income               #
#                    - Considers selling land to developer based on age       #
#                    - Considers selling land based on proximity to urban     #
#                      environment                                            #
#                    - Decides whether to sell                                #
#                    - Decides whether to switch crop choice                  #
#                                                                             #
#=============================================================================#
   



# This will come in handy: https://stackoverflow.com/questions/4877624/numpy-array-of-objects


class Farmer:
    def __init__(self, Age, CropID, CropYield, CropPrice, AreaCultivated, 
                 PreHarvestEnergyCosts, PreHarvestLaborCosts, PreHarvestMaterialCosts, 
                 HarvestEnergyCosts, HarvestLaborCosts, HarvestMaterialCosts,
                 DistFromCity, OffFarmIncome):
        
        self.Age = Age
        self.CropID = CropID
        self.CropYield = CropYield
        self.CropPrice = CropPrice
        self.AreaCultivated = AreaCultivated
        
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
        
        self.DistFromCity = DistFromCity
        self.OnFarmIncome = self.AreaCultivated * self.CropYield * self.CropPrice
        self.OffFarmIncome = OffFarmIncome

    # Set/Update functions

    def UpdateAge(self):
        self.Age += 1
        
    def UpdateDistFromCity(self,dx):
        self.DistFromCity += dx
    
    def UpdateOnFarmIncome(self, NewAreaCultivated=None, NewCropYield=None, NewCropPrice=None):
        self.AreaCulttivated  = NewAreaCult if NewAreaCult is not None else self.AreaCultivated
        self.CropYield = NewCropYield if NewCropYield is not None else self.CropYield
        self.CropPrice = NewCropPrice if NewCropPrice is not None else self.CropPrice
        self.OnFarmIncome = NewAreaCult * NewCropYield * NewCropPrice
        
    def UpdateOnFarmCosts(self, NewPreHarvestEnergyCosts=None, NewPreHarvestLaborCosts=None, 
                          NewPreHarvestMaterialCosts=None, NewHarvestEnergyCosts=None, 
                          NewHarvestLaborCosts=None, NewHarvestMaterialCosts=None):
        # Update preharvest costs
        self.PreHarvestEnergyCosts    = NewPreHarvestEnergyCosts if NewPreHarvestEnergyCosts is not None else self.PreHarvestEnergyCosts
        self.PreHarvestLaborCosts     = NewPreHarvestLaborCosts if NewPreHarvestLaborCosts is not None else self.PreHarvestLaborCosts 
        self.PreHarvestMaterialCosts  = NewPreHarvestMaterialCosts if NewPreHarvestMaterialCosts is not None else self.PreHarvestMaterialCosts 
        
        self.PreHarvestCosts = self.PreHarvestEnergyCosts + self.PreHarvestLaborCosts + PreHarvestMaterialCosts
        
        # Update harvest costs
        self.HarvestEnergyCosts    = NewHarvestEnergyCosts if NewHarvestEnergyCosts is not None else self.HarvestEnergyCosts
        self.HarvestLaborCosts     = NewHarvestLaborCosts if NewHarvestLaborCosts is not None else self.HarvestLaborCosts 
        self.HarvestMaterialCosts  = NewHarvestMaterialCosts if NewHarvestMaterialCosts is not None else self.HarvestMaterialCosts 

        self.HarvestCosts = self.HarvestEnergyCosts + self.HarvestLaborCosts + self.HarvestMaterialCosts
 
        self.Costs = self.PreHarvestCosts + self.HarvestCosts
        self.TotalCosts = self.AreaCultivated * self.Costs
        
    def UpdateOffFarmIncome(self,loc=0.0,scale=1.0):
        self.OffFarmIncome *= scale
        self.OffFarmIncome += loc
        
    def EvaluateAlternativeCrop(self, AltCropID, AltAreaCult=None, AltCropYield, AltCropPrice):
        AltAreaCult = AltAreaCult if AltAreaCult is not None else self.AreaCultivated
        AltOnFarmIncome = AltAreaCult * AltCropYield * AltCropPrice
        
    def Decide(self)
        
        