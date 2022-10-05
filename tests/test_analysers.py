"""
Tests for the module with parsers.
Part of package hvec_tide.
Created by HVEC, May 2022
"""

# Public packages
import pytest as pyt
import pandas as pd
import utide as ut
import os

# Company packages
import hvec_tide as tide


def test_run_utide_solve():
    df = pd.read_excel(r'./tests/data_sample.xlsx')
    t = df['tepoch']
    h = df['h']
    sol = tide.run_utide_solve(t, h, lat = 52, verbose = False)
    return


def test_constit_segment():
    df = pd.read_excel(r'./tests/data_sample.xlsx')
    tide.constit_segment(
        df,
        col_datetime = 'datetime',
        col_h = 'h', include_phase = True,
        lat = 52
    )  
    return


def test_tide_and_setup():
    df = pd.read_excel(r'./tests/data_sample.xlsx')
    time = df['datetime']
    h = df['h']

    tide.tide_and_setup(time, h, lat = 52)
    return


def test_analyse_long_series():
    df = pd.read_excel(r'./tests/data_sample.xlsx')
    df, constit = tide.analyse_long_series(df, lat = 52, trend = False, include_phase = False, delta_T = 'Y')
    return
