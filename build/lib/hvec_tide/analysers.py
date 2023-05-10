"""
Module with analysers in addition to harmonic analysis of tides.
Part of package hvec_tide.
Created by HVEC, May 2022
"""

# Public packages
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
import utide as ut

# Company packages
from hvec_stat import goodness_of_fit as gof
from hvec_tide import parsers as parse
from hvec_tide import analysers as tide

tqdm.pandas()


def select_constituents(df, latitude, settings, thr = 99):
    """
    Select constituents based on a tidal analysis of the last year in the set.
    Take the constituents, ordered by percentage of energy (PE), and select the constituents of
    which the summed PE reaches a specified threshold.

    Args:
        df, dataframe with observations
        latitude, float. Required argument of UTide
        settings, dictionary with the following fields:
            nameColumn, timeColumn and levelColumn; all string. Specifying the names
            of the name, time and level columns respectively
    
    Returns:
        selected constituents as a list of strings
    """
    #TODO specify more methods for selecting constituents; primarily prescribed sets
    name = df[settings['nameColumn']].unique().squeeze()
    logging.info(f'Selecting constituents with threshold {thr} % for {name}')

    time = settings['timeColumn']
    level = settings['levelColumn']
    
    try:
        coef = tide.run_utide_solve(
            df[time], df[level],
            lat = latitude,
            nodal = False, trend = False, verbose = False)

        # Select constituent set based on summed PE threshold
        idMx = (coef.PE.cumsum() > thr).argmax()
        selected = coef.name[:idMx].tolist()
        return selected
    except:
        return ['Error raised']


def run_utide_solve(t, h, meth_N = 'Bence', verbose = False, **kwargs):
    """
    Apply data quality control and error checking
    before and after running ut.solve.

    Add additional statistical output to result of Utide.
    """
    try:
        sol = ut.solve(t, h, verbose = verbose, **kwargs)
    except Exception as e:
        logging.warning(e)
        sol = str(e)
        return sol

    sol.zmean = h.mean()
    sol.count = h.count()

    # Generate statistical info
    hmodel = ut.reconstruct(t, sol, verbose = verbose).h

    k = len(sol.A) * 2 + 1  # Number of parameters used
    if 'trend' in kwargs.keys():
        if kwargs['trend']:
            k+=1

    Rsq_adj = gof.Rsq_adj(ydata = h, ymodel = hmodel, k = k, method = meth_N)
    sol.Rsq_adj = Rsq_adj
    sol.correlation_method = meth_N

    # Add wind effects to result
    s = h - hmodel
    sol.smean = s.mean()
    sol.smin = s.min()
    sol.smax = s.max()
    return sol


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
    t = time

    # Run harmonic analysis, if not provided
    if sol == 'none':
        logging.info('No Utide result provided. Running Utide')

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
    t = df[col_datetime]

    # Create utide bunch object
    sol = run_utide_solve(
        t, df[col_h], **kwargs
    )

    if isinstance(sol, str):
        return
 
    h_astr, s, _, _, _ = tide_and_setup(
        df[col_datetime], df[col_h], sol = sol, **kwargs
    )

    # Augment time series
    df['h_astr'], df['setup'] = h_astr, s
    return df


def _constit_segment(
    df,
    col_datetime,
    col_h, include_phase = False,
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
    
    t = df[col_datetime]

    # Create utide bunch object
    sol = run_utide_solve(
        t, df[col_h], **kwargs
    )
    if isinstance(sol, str):
        return

    constit = parse.parse_utide(
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
    create_time_series = False,
    include_phase = False, **kwargs):
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
    logging.info('Running tide analysis of long series')

    gr = df.groupby([
        pd.Grouper(freq = delta_T, key = col_datetime),
        pd.Grouper(col_loc)], group_keys = False)  # group_keys added to silence deprecation warning

    constit = gr.progress_apply(
        lambda gr: _constit_segment(
            gr, col_datetime, col_h, 
            include_phase = include_phase, **kwargs)
     )

    constit.reset_index(inplace = True)  # Turn created multi-index into columns

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

    return pd.DataFrame(), constit
