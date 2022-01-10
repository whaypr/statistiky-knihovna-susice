import os
import urllib
from bidict import bidict

import time
import datetime

import pandas as pd

try:
    from app.parsing import update_data # in heroku
except:
    from parsing import update_data # locally


# GLOBAL VARS
years = [year for year in range(2015, 2021)]

data_url = 'https://susice.tritius.cz/statistics'
topics_days = ['access', 'login', 'search']
topics_months = ['rating', 'summary']


# DATA
    # monthly
summary = {
    year: pd.read_csv(os.path.join('data', 'months', f'summary_{year}.csv'), header=[0,1], index_col=0)
    for year in years
}
rating = {
    year: pd.read_csv(os.path.join('data', 'months', f'rating_{year}.csv'), header=[0,1], index_col=0)
    for year in years
}

    # daily
access = {
    f'{year}:{month}': pd.read_csv(os.path.join('data', 'days', f'{year}', f'access_{year}_{month}.csv'), index_col=0)
    for year in years
    for month in range(1,13)
}
login = {
    f'{year}:{month}': pd.read_csv(os.path.join('data', 'days', f'{year}', f'login_{year}_{month}.csv'), index_col=0)
    for year in years
    for month in range(1,13)
}
search = {
    f'{year}:{month}': pd.read_csv(os.path.join('data', 'days', f'{year}', f'search_{year}_{month}.csv'), index_col=0)
    for year in years
    for month in range(1,13)
}


# PERIODIC DATA UPDATE
def update_library_data():
    while True:
        date = datetime.datetime.now()
        year = date.year
        month = date.month

        update_data(data_url, topics_days, topics_months, year, month)

        # monthly data update
        summary[year] = pd.read_csv(os.path.join('data', 'months', f'summary_{year}.csv'), header=[0,1], index_col=0)
        rating[year] = pd.read_csv(os.path.join('data', 'months', f'rating_{year}.csv'), header=[0,1], index_col=0)
        # daily data update
        access[f'{year}:{month}'] = pd.read_csv(os.path.join('data', 'days', f'{year}', f'access_{year}_{month}.csv'), index_col=0)
        login[f'{year}:{month}'] = pd.read_csv(os.path.join('data', 'days', f'{year}', f'login_{year}_{month}.csv'), index_col=0)
        search[f'{year}:{month}'] = pd.read_csv(os.path.join('data', 'days', f'{year}', f'search_{year}_{month}.csv'), index_col=0)

        time.sleep(60 * 60) # in seconds
