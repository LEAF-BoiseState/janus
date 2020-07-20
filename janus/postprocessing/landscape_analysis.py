"""
Created on Tue July 20 2020

@author: kendrakaiser

Suite of functions to evaluate heterogeneity of landscape
"""

import pylandstats as pls


def lc_analysis(lc, scale):
    """
    :param lc:      stack of land cover data
    :type lc:       numpy

    :param scale:   resolution of grid
    :type scale:    int

    :return:        figures and csv of analysis
    """

    ls = pls.Landscape(lc)
    # TODO: evaluate which subset of metrics are of most importance to cut down on compute time
    patch_metrics_df = ls.compute_patch_metrics_df()
    crop_totals = patch_metrics_df['class_val'].value_counts()
    class_metrics_df = ls.compute_class_metrics_df()
    landscape_metrics_df = ls.compute_landscape_metrics_df()
