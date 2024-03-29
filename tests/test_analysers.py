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
from datetime import datetime as dt

# Company packages
import hvec_tide as tide


df = pd.read_excel(r'./tests/data_sample.xlsx')


def test_select_constituents():
    settings = {
        'nameColumn': 'naam'
        , 'timeColumn': 'datetime'
        , 'levelColumn': 'h'
    }
    coef = tide.analysers.select_constituents(df, latitude = 52, settings = settings)
    assert len(coef) > 2
    assert 'M2' in coef
    assert 'S2' in coef


def test_run_utide_solve():
    t = df['datetime']
    h = df['h']
    sol = tide.run_utide_solve(t, h, lat = 52, verbose = False)
    assert len(sol.name) > 0


def test_constit_segment():
    sol = tide.analysers._constit_segment(
        df,
        col_datetime = 'datetime',
        col_h = 'h', include_phase = True,
        lat = 52
    )
    assert len(sol.columns) > 0


def test_tide_and_setup():
    time = df['datetime']
    h = df['h']

    sol = tide.tide_and_setup(time, h, lat = 52)
    assert len(sol) > 0


def test_analyse_long_series():
    start = dt.now()
    _, constit = tide.analyse_long_series(
        df, lat = 52, trend = False, include_phase = False, delta_T = 'Y', verbose = False)
    end = dt.now()
    print(end - start)
    assert len(constit.columns) > 0
