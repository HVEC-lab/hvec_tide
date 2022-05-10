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
import hvec_tide.analysers as tide

df = pd.read_excel(r'./tests/data_sample.xlsx')


def test_tide_and_setup():
    time = df['datetime']
    h = df['h']

    tide.tide_and_setup(time, h, lat = 52)
    return


def test_analyse_long_series():
    df, constit = tide.analyse_long_series(df, lat = 52)
    return
