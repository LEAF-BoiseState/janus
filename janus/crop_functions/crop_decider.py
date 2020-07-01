"""
Created on Tue Jul  9 12:12:43 2019

@author: lejoflores & kendrakaiser

Suite of functions to make decisions about what crop to plant
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
    """ Creates probability curves that show likelihood of switching crops based on profits
    :param alpha:       Alpha parameter for the incomplete beta distribution
    :param beta:        Beta parameter for the incomplete beta distribution
    :param fmin:        Fraction of current profit at which the CDF of the beta distribution is zero
    :param fmax:        Fraction of current profit at which the CDF of the beta distribution is one
    :param n:           Number of points to generate in the CDF
    :param profit:      Current profit

    :return:            Two (n x 1) numpy arrays containing, respectively n points spaced
                        linearly between fmin*profit and fmax*profit (x2) and the associated points
                        of the beta distribution as specified by alpha and beta (fx).
    """
    x = np.linspace(0, 1.0, num=n)

    fx = sp.betainc(alpha, beta, x)

    x2 = np.linspace(fmin * profit, fmax * profit, num=n)

    return x2, fx


def decide2switch(alpha, beta, fmin, fmax, n, profit, profit_p):
    """ This decides whether to retain current crop or switch to one other option

    :param alpha: The alpha parameter for the incomplete beta distribution
    :param beta: The beta parameter for the incomplete beta distribution
    :param fmin: The fraction of current profit at which the CDF of the beta distribution is zero
    :param fmax: The fraction of current profit at which the CDF of the beta distribution is one
    :param n: The number of points to generate in the CDF 
    :param profit: The current profit the farmer experiences
    :param profit_p: The potential profit of the alternative crop being evaluated

    :return: A binary flag indicating whether or not to switch crops (1 = switch, 0 = do not switch)

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


def assess_profit(crop, profits_current, profit_signals, num_crops, crop_ids):
    """Get the potential profits from the next time step and set the last profit equal to the current profit

   :param crop:             Current crop choice
   :type crop:              Int

   :param profits_current:  Profit from current crop choice
   :type profits_current:   Float

   :param profit_signals:   A vector of profits against which current profit will be assessed
   :type profit_signals:    Vector

   :param num_crops:        The number of crops in the vector of Profit_signals
   :type num_crops:         Int

   :param crop_ids:          The associated vector of crop IDs associated with the input profit signal
   :param crop_ids:          Vector

   :return:                 Float of the profit for a particular crop (Crop) from the last time step, \
                            and an array of potential profits for the current time step
    :type:                  Float and Vector

   """

    # Existing Crop ID
    cur_crop_choice_ind = crop.astype('int')

    # assess current and future profit of that given crop
    if np.isin(cur_crop_choice_ind, crop_ids):  # if the current land cover is a crop
        profit_last = profits_current  # last years profit in this location
        profit_expected = profit_signals.reshape(num_crops, 1)  # next years anticipated profit

    else:
        profit_last = 0
        profit_expected = np.zeros((num_crops, 1))

    return profit_last, profit_expected


def profit_maximizer(alpha, beta, fmin, fmax, n, profits_current, vec_crops, vec_profit_p, rule=True):
    """ Decide which crop and associated profit to pick out of N options.

    :param alpha:           Alpha parameter for the incomplete beta distribution
    :type alpha:            Float

    :param beta:            Beta parameter for the incomplete beta distribution
    :type beta:             Float

    :param fmin:            Fraction of current profit at which the CDF of the beta distribution is zero
    :type fmin:             Int

    :param fmax:            Fraction of current profit at which the CDF of the beta distribution is one
    :type fmax:             Int

    :param n:               Number of points to generate in the CDF
    :type n:                Int

    :param profits_current: Current profit
    :type profits_current:  Float

    :param vec_crops:       A vector of potential alternative crops
    :type vec_crops:        Number of crops x1 vector

    :param vec_profit_p:    A vector of potential profits associated with the alternatives contained in vec_crops
    :type vec_profit_p:     Number of crops x1 vector

    :param rule:            A boolean indicating whether, if multiple alternative crops are viably
                            more profitable, to choose the most profitable alternative (True),
                            or select randomly between all viable alternatives.

    :return:                Integer denoting crop choice and float of the associated profit
    :type:                  Int and float
    """
    # Key assumptions: the vector of crop IDs and anticipated profits associated
    # with each crop must both be N x 1 column vectors.
    assert (vec_crops.shape == vec_profit_p.shape), \
        'Supplied vector of crop IDs and potential profits must be identical'
    assert (vec_crops.shape[1] == 1), \
        'Supplied vector of crop IDs and potential profits must be N x 1'

    # Create a boolean vector to store a 0 or 1 if the farmer will select the
    # crop (==1) or not (==0)
    AccRej = np.zeros(vec_crops.shape, dtype='int')

    for i in np.arange(AccRej.size):
        # Determine whether or not the crop is viable
        AccRej[i] = decide2switch(alpha, beta, fmin, fmax, n, profits_current,
                           vec_profit_p[i])

    # Find the Crop IDs and associated profits that were returned as "viable": decide2switch came back as "yes" == 1
    ViableCrops = vec_crops[AccRej == 1]
    ViableProfits = vec_profit_p[AccRej == 1]

    if (ViableCrops.size == 0):
        return -1, -1

    # Find the maximum anticipated profit and the crop IDs associated with that
    MaxProfit = ViableProfits.max()
    MaxProfitCrop = ViableCrops[ViableProfits == MaxProfit]

    # This should be rare: if there happen to be more than one viable
    # crops that carry the same anticipated profit that also coincides with
    # the maximum anticipated profit. The choice here is to choose randomly
    # from among those crops that have the same maximum profit
    if (MaxProfitCrop.size > 1):
        ViableCrops = MaxProfitCrop
        ViableProfits = ViableProfits[ViableProfits == MaxProfit]
        rule = False  # Switch rule to make the algorithm using the random option

    if (rule):  # Return crop with largest profit
        CropChoice = MaxProfitCrop
        ProfitChoice = MaxProfit

    else:  # Choose randomly from among all viable crops
        indChoice = np.random.choice(np.arange(ViableCrops.size), size=1)
        CropChoice = ViableCrops[indChoice]
        ProfitChoice = ViableProfits[indChoice]

    # Return the crop choice and associated profit
    return CropChoice, ProfitChoice


def make_choice(crop_id_last, profit_last, crop_choice, profit_choice, seed=False):
    """ Compare the crop choice with associated profit, set the new crop ID if switching, add variability to the
            anticipated profit

    :param crop_id_last:        The crop choice from the last time step
    :type crop_id_last:         Int

    :param profit_last:         The profit from the last time step associated with that crop
    :type profit_last:          Float

    :param crop_choice:         A flag indicating whether the new crop is selected
    :type crop_choice:          Int

    :param profit_choice:       A flag indicating whether there is a profitable alternative
    :type profit_choice:        Int

    :param seed:                A boolean indicating whether or not to use a random seed
    :type seed:                 Bool

    :return:                    The new crop ID and its associated profit
    :type:                      Int and Float
    """

    if seed:

        try:
            seed_val
        except NameError:
            print("Random seed needs to be initialized using the CropDecider.DefineSeed() Function")

        np.random.seed(seed_val)

    # Check if return  values indicate the farmer shouldn't switch
    if (crop_choice == -1) and (profit_choice == -1):
        crop_id_next = crop_id_last
        profit_act = profit_last + np.random.normal(loc=0.0, scale=1000.0, size=(1, 1, 1))  # this years actual profit

    else:  # switch to the new crop and add variability to resulting profit
        crop_id_next = crop_choice
        profit_act = profit_choice + np.random.normal(loc=0.0, scale=1000.0, size=(1, 1, 1))

    return crop_id_next, profit_act
