"""
Module with analysers in addition to harmonic analysis of tides.
Part of package hvec_tide.
Created by HVEC, May 2022
"""

# Public packages
import utide as ut
import numpy as np
import datetime as dt
import pandas as pd
import copy as cp
from tqdm import tqdm
import logging


# Company packages
import hvec_tide as tide
import hvec_stat.gof as gof


tqdm.pandas()
logging.basicConfig(
    filename = 'hvec_tide.log',
    level = logging.INFO,
    encoding = 'utf-8',
    filemode = 'w'
)


def run_utide_solve(t, h, meth_N = 'Bence', **kwargs):
    """
    Apply data quality control and error checking
    before and after running ut.solve
    """
    try:
        sol = ut.solve(
            t, h, verbose = False,
            **kwargs
        )
    except:
        logging.warning(
            'Utide solve did not run succesfully'
        )
        sol = 'Utide failed'
        return sol

    sol.zmean = h.mean()
    sol.count = h.count()

    # Generate statistical info
    hmodel = ut.reconstruct(t, sol, verbose = False).h
    k = len(sol.A) * 2 + 1  # Number of parameters used
    if kwargs['trend']: k+=1

    Rsq_adj = gof.Rsq_adj(
        ydata = h,
        ymodel = hmodel,
        k = k,
        method = meth_N
        )
    sol.Rsq_adj = Rsq_adj
       
    return sol


def _create_tepoch(time):
    """
    Ensure consistency in calculating tepoch by
    providing a single function for it.
    """
    tepoch = (
        (time - dt.datetime.utcfromtimestamp(0)).
        dt.total_seconds()/86400
        )
    return tepoch


def tide_and_setup(
    time, h, sol = 'none', 
    meth_N = 'Bence', **kwargs):
    """
    Take a time series of water levels and return the wind effect,
    defined as the difference between observed and calculated (harmonic)
    level.

    Parameters
    -------
    time: time in datetime format
    h: water level
    sol, optional: utide output Bunch. A specific Utide object
    *args, **kwargs: arguments for optional run of Utide

    Returns
    -------
    h_astr, arraylike: calculated astronomical tide
    s, arraylike: calculated wind effect for every time in the set
    s_mean, s_min, s_max, float: mean, minimum and maximum setup
        in the set

    Issues
    --------
    None
 
    References
    --------
    Codiga, Daniel. (2011). Unified tidal analysis and 
        prediction using the UTide Matlab functions. 10.13140/RG.2.1.3761.2008
    
    Pugh, D. and P. Woodworth - Sea level science;
        Cambridge University Press, 2014
    """

    # Create time with respect to epoch
    t = _create_tepoch(time)

    # Run harmonic analysis, if not provided
    if sol == 'none':
        print('No Utide result provided. Running Utide')        
        
        sol = run_utide_solve(
            t, h, method = meth_N, verbose = False,
            **kwargs
        )
    
    if sol == 'Utide failed':
        return
    
    # Calculate astronomic water level
    h_astr = ut.reconstruct(t, sol, verbose = False).h

    # Calculate wind effect
    s = np.array(h - h_astr)

    # Calculate statistics of wind effect
    s_mean = s.mean()
    s_min = s.min()
    s_max = s.max()

    return h_astr, s, s_min, s_mean, s_max


def _timeseries_segment(
    df,
    col_datetime,
    col_h,
    **kwargs
    ):
    """
    Run tidal analysis for a single group provided by
    function analyse_long_series and add astronomical
    tide and wind setup to the timeseries.

    **kwargs takes all arguments for utide. 
    lat should be provided!
    """

    # First create vector of tepoch
    t = _create_tepoch(df[col_datetime])

    # Create utide bunch object
    sol = run_utide_solve(
        t, df[col_h], **kwargs
    )

    if sol == 'Utide failed':
        return
 
    h_astr, s, s_min, s_mean, s_max = tide_and_setup(
        df[col_datetime], df[col_h], sol = sol, **kwargs
    )

    # Augment time series
    df['h_astr'], df['setup'] = h_astr, s
    return df


def constit_segment(
    df,
    col_datetime,
    col_h, include_phase,
    include_char_levels = False,
    include_freq = False,
    **kwargs
    ):    
    """
    Run tidal analysis for a single group provided by
    function analyse_long_series and create table of
    the tidal constituents in the segment.

    **kwargs takes all arguments for utide. 
    lat should be provided!
    """
    
    # First create vector of tepoch
    t = _create_tepoch(df[col_datetime])

    # Create utide bunch object
    sol = run_utide_solve(
        t, df[col_h], **kwargs
    )
    if sol == 'Utide failed':
        return

    constit = tide.parse_utide(
        sol, include_phase=include_phase,
        include_freq = include_freq,
        include_char_levels = include_char_levels)
    return constit


def analyse_long_series(
    df,
    col_datetime = 'datetime',
    col_h = 'h',
    col_loc = 'naam',
    delta_T = 'Y',
    create_time_series = True,
    include_phase = True,
    *args, **kwargs):
    """
    Takes a dataframe with at least:
        - datetime field
        - water level field
    
    Analyse it seperating the data according to time with
    interval specified on input.
    
    Parameters
    -------
    df: dataframe with water level observations
    col_datetime: name of the datetime column
    col_h: name of the water level column
    delta_T: time interval specified for a pd.Grouper object

    Returns
    -------
    df: original dataframe augmented with astronomic water level
        and wind setup
    constit: dataframe containing the tidal constituents for the
        groups specified according to delta_T

    Issues
    --------
    None
 
    References
    --------
    Codiga, Daniel. (2011). Unified tidal analysis and 
        prediction using the UTide Matlab functions. 10.13140/RG.2.1.3761.2008
    
    Pugh, D. and P. Woodworth - Sea level science;
        Cambridge University Press, 2014
    """

    gr = df.groupby([
        pd.Grouper(freq = delta_T, key = col_datetime),
        pd.Grouper(col_loc)])
        
    constit = gr.progress_apply(
        lambda gr: constit_segment(
            gr, col_datetime, col_h, 
            include_phase = include_phase, **kwargs)
     )

    if create_time_series:
        res = gr.progress_apply(
            lambda gr: _timeseries_segment(
                gr, col_datetime, col_h, **kwargs
                )
            )

        # Grouping used to analyse the tide per period. Once
        # the tide has been reconstructed, the index resulting
        # from grouping can be dropped.
        res.reset_index(drop = True, inplace = True)

        return res, constit
    else:
        return constit