"""
Module with parsers for harmonic analysis of tides.
Part of package hvec_tide.
Created by HVEC, May 2022
"""


import pandas as pd
import numpy as np


def parse_utide(
    sol, include_char_levels = True,
    include_phase = True,
    include_freq = False
    ): 
    """
    Parse the result of a harmonic analysis to a dataframe
    with all results in a single row and the variable names
    as columns.
    
    UTide can be run with several options. Therefore some
    parsing is conditional.

    Parameters
    -------
    sol: utide output Bunch. A specific Utide object
    include_freq: include the frequency of the reported tidal
        constituents. Is textbook so False is default

    Returns
    -------
    df: dataframe

    Issues
    --------
    None
 
    References
    --------
    NA
    """

    data = []
    names = []

    names = np.hstack([names, 'z0'])
    data = np.hstack([data, sol.mean])

    names = np.hstack([names, sol.name + '_ampl'])
    data = np.hstack([data, sol.A])

    if include_phase:
        names = np.hstack([names, sol.name + '_phase'])
        data = np.hstack([data, sol.g])

    if 'slope' in sol.keys():
        names = np.hstack([names, 'slope'])
        data = np.hstack([data, sol.slope])

    if 'rms_resid' in sol.keys():
        names = np.hstack([names, 'rms_resid'])
        data = np.hstack([data, sol.rf.rms_resid])
    
    if 'A_ci' in sol.keys():
        names = np.hstack([names, sol.name + '_A_ci'])
        data = np.hstack([data, sol.A_ci])

    if ('g_ci' in sol.keys()) and (include_phase):
        names = np.hstack([names, sol.name + '_g_ci'])
        data = np.hstack([data, sol.g_ci])

    if include_freq:
        names = np.hstack([names, sol.name + '_frq'])
        data = np.hstack([data, sol.aux.frq])

    res = pd.DataFrame(
        columns = names,
        data = [data]
    )

    if include_char_levels:
        res = parse_characteristic_levels(res)

    return res


def parse_characteristic_levels(df):
    """
    Take a parsed result of Utide and calculate
    characteristic tide levels from it.

    Parameters
    -------
    df: dataframe in the format provided by parse_utide

    Returns
    -------
    df, augmented with the following columns:
        'MLWS', 'MLWN', 'MHWN' and 'MHWS'

    Issues
    --------
    None
 
    References
    --------
    NA
    """
    
    df['MHWS'] = df['z0'] + df['M2_ampl'] + df['S2_ampl']
    df['MLWS'] = df['z0'] - df['M2_ampl'] - df['S2_ampl']
    df['MHWN'] = df['z0'] + df['M2_ampl'] - df['S2_ampl']
    df['MLWN'] = df['z0'] - df['M2_ampl'] + df['S2_ampl']

    return df