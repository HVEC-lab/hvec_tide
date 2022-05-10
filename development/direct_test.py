import pandas as pd
import os
import time

import hvec_tide.analysers as tide


os.chdir(os.path.dirname(os.path.realpath(__file__)))

df = pd.read_excel(r'data_sample.xlsx')

out = tide.analyse_long_series(df, lat = 52, delta_T = 'Y', constit='auto')

time.sleep(3600)