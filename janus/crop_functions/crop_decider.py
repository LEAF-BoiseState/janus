"""
Created on Tue Jul  9 12:12:43 2019

@author: lejoflores
"""

import numpy as np
import scipy.special as sp


def define_seed(seed):
    """ Creates seed for random selection for testing
    :param seed:            Seed value

    :return:                Global seed value

    """
    global seed_val

    seed_val = seed

    return


def switching_prob_curve(alpha, beta, fmin, fmax, n, profit):
    """ Creates probability curves that show likelyhood of switching crops based on profits"
    :param alpha:
    :param beta:
    :param fmin:
    :param fmax:
    :param n:
    :param profit:

    :return:

    """
    x = np.linspace(0, 1.0, num=n)

    fx = sp.betainc(alpha, beta, x)

    x2 = np.linspace(fmin * profit, fmax * profit, num=n)

    return x2, fx


def decide(alpha, beta, fmin, fmax, n, profit, profit_p):
    """ This decides whether to retain current crop or switch to one other option

    :param alpha:
    :param beta:
    :param fmin:
    :param fmax:
    :param n:
    :param profit:
    :param profit_p:

    :return:

    """
    if profit_p > profit:

        x, fx = switching_prob_curve(alpha, beta, fmin, fmax, n, profit)

        prob_switch = np.interp(profit_p, x, fx)

        if (np.random.rand(1) < prob_switch):  # need to send it seed in the unit test
            return 1  # Switch
        else:
            return 0  # Do not switch

    else:
        return 0  # Do not switch if not profitable


def decide_n(alpha, beta, fmin, fmax, n, Profits_current, vec_crops,
            vec_profit_p, rule=True):
    """Decide which crop and associated profit to pick out of two options.

    :param alpha:
    :param beta:
    :param fmin:
    :param fmax:
    :param n:
    :param current_profit:
    :param vec_crops:
    :param vec_profit_p:
    :param rule:

    :return: integer denoting crop choice and float of the associated profit
    """

    # Key assumptions: the vector of crop IDs and anticipated profits associated
    # with each crop must both be N x 1 column vectors. Error trap this below:
    assert (vec_crops.shape == vec_profit_p.shape), \
        'Supplied vector of crop IDs and potential profits must be identical'
    assert (vec_crops.shape[1] == 1), \
        'Supplied vector of crop IDs and potential profits must be N x 1'

    # Create a boolean vector to store a 0 or 1 if the farmer will select the
    # crop (==1) or not (==1)
    AccRej = np.zeros(vec_crops.shape, dtype='int')

    for i in np.arange(AccRej.size):
        # Use the `Decide` function above to choose whether or not the crop is
        # viable
        AccRej[i] = decide(alpha, beta, fmin, fmax, n, Profits_current,
                           vec_profit_p[i])  # is fmin/fmax setting bounds on range of additional profit?

    # Find the Crop IDs and associated profits that were returned as "viable"
    # based on the "Decide" function (that is, Decide came back as "yes" == 1)
    ViableCrops = vec_crops[AccRej == 1]
    ViableProfits = vec_profit_p[AccRej == 1]

    if (ViableCrops.size == 0):
        return -1, -1

    # Find the maximum anticipated profit and the crop IDs associated with that
    # maximum
    MaxProfit = ViableProfits.max()
    MaxProfitCrop = ViableCrops[ViableProfits == MaxProfit]

    # This next part should be rare. There happen to be more than one viable
    # crops that carry the same anticipated profit that also coincides with
    # the maximum anticipated profit. The choice here is to choose randomly
    # from among those crops that have the same (maximum) profit
    if (MaxProfitCrop.size > 1):
        ViableCrops = MaxProfitCrop
        ViableProfits = ViableProfits[ViableProfits == MaxProfit]
        rule = False  # Switch rule to trick the algorithm into using the random option

    if (rule):  # Return crop with largest profit
        CropChoice = MaxProfitCrop
        ProfitChoice = MaxProfit

    else:  # Choose randomly from among all viable crops
        indChoice = np.random.choice(np.arange(ViableCrops.size), size=1)
        CropChoice = ViableCrops[indChoice]
        ProfitChoice = ViableProfits[indChoice]

    # Return the crop choice and associated profit
    return CropChoice, ProfitChoice


def assess_profit(Crop, Profits_current, Profit_signals, Num_crops, CropIDs):
    """Decide which crop and associated profit to pick out of two options.

   :param Crop:                    Current Crop Choice
   :param Profits_current:         Profit from current crop choice
   :param Profits_expected:
   :param Num_crops:
   :param CropIDs:

   :return: integer denoting crop choice and float of the associated profit

   """

    # Existing Crop ID
    CurCropChoice_ind = Crop.astype('int')
    # CropIx=np.where(CropIDs == CurCropChoice_ind)# crop ID lookup
    # assess current and future profit of that given crop
    if np.isin(CurCropChoice_ind, CropIDs):  # if the current landcover is a crop
        Profit_last = Profits_current  # last years profit in this location
        Profit_expected = Profit_signals.reshape(Num_crops, 1)

    else:
        Profit_last = 0
        Profit_expected = np.zeros((Num_crops, 1))

    return Profit_last, Profit_expected


def make_choice(CropID_last, Profit_last, CropChoice, ProfitChoice, seed=False):
    """

    :param CropID_last:
    :param Profit_last:
    :param CropChoice:
    :param ProfitChoice:
    :param seed:

    :return:
    """

    if seed:

        try:
            seed_val
        except NameError:
            print("Random seed needs to be initialized using the CropDecider.DefineSeed() Function")

        np.random.seed(seed_val)

    # Check if return  values indicate the farmer shouldn't switch
    if (CropChoice == -1) and (ProfitChoice == -1):
        CropID_next = CropID_last
        Profit_act = Profit_last + np.random.normal(loc=0.0, scale=1000.0, size=(1, 1, 1))  # this years actual profit

    else:  # switch to the new crop
        CropID_next = CropChoice
        Profit_act = ProfitChoice + np.random.normal(loc=0.0, scale=1000.0, size=(1, 1, 1))

    return CropID_next, Profit_act
