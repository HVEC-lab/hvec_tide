"""
Tests for the module with parsers.
Part of package hvec_tide.
Created by HVEC, May 2022
"""

# Public packages
import pytest as pyt
import pandas as pd
#import utide as ut
import math

# Company packages
import hvec_tide as tide


df = pd.read_excel(r'./tests/data_sample.xlsx')


@pyt.mark.parametrize(
    "lat, trend, conf_int, method, nodal, incl_freq",
    [   (52, False, 'none', 'ols', False, False),
        (52, False, 'linear', 'ols', False, True),
        (52, False, 'MC', 'ols', False, False),
        (52, True, 'none', 'ols', False, False),
        (52, False, 'none', 'robust', False, False),
        (52, False, 'none', 'ols', True, False),
        (52, False, 'none', 'ols', False, True),
    ]
)
#TODO: Utide version 0.3.0 causes errors. Returned to 0.2.6
def test_parse_utide(
    lat, trend, conf_int, method, nodal, incl_freq 
):
    """
    Test parser for a number of configurations of Utide
    """
    t = df['tepoch']
    h = df['h']
    
    coef = tide.run_utide_solve(
        t, h,
        lat = lat,
        trend = trend,
        conf_int = conf_int,
        method = method,
        nodal = nodal, verbose = True
    )

    result = tide.parse_utide(coef, incl_freq)
    assert len(result) > 0


def test_parse_characteristic_levels():
    df = pd.DataFrame(
        columns = ['z0', 'M2_ampl', 'S2_ampl'],
        data = [[0.05, 0.79, 0.02]])

    df = tide.parsers._parse_characteristic_levels(df)
    assert (
        math.isclose(df['MLWS'], -0.76) and
        math.isclose(df['MLWN'], -0.72) and
        math.isclose(df['MHWN'], 0.82) and
        math.isclose(df['MHWS'], 0.86)
        )

