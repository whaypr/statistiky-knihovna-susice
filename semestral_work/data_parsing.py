import pandas as pd

import requests
from bs4 import BeautifulSoup
import re


def get_dataframes_months(url, topics, years):
    # get links to subsites with months data for given topics and years
    links = [f'{url}/{topic}/{year}' for topic in topics for year in years]

    # loop through all links and parse data from them into dataframes
    dataframes_months = []
    for link in links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        table = soup.find("table")
        df = pd.read_html(str(table), index_col=0)[0]
        #df.columns.set_levels([df.columns[3*i][0] + ' ' + link[-4:] for i in range(len(df.columns.levels[0]))], level=0, inplace=True)
        dataframes_months.append(df)
    
    return dataframes_months


def get_dataframes_days(url, topics, years):
    # get links to subsites with days data for given topics and years
    links = [f'{url}/{topic}/{year}/{month}' for topic in topics for year in years for month in range(1,13)]

    # loop through all links and parse data from them into dataframes
    dataframes_days = []
    for link in links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        text = str(soup.find_all('script')[3])

        mod = 'total' # total, internal or external
        m = re.search(f'{mod}.*\'data\':\[([^\]]+)\]', text)

        data = enumerate(m.group(1).split(','), start=1)
        df = pd.DataFrame(data, columns=['Den', 'Počet']) 
        df.set_index('Den', inplace=True)

        dataframes_days.append(df)

    return dataframes_days


def save_months_to_csv(dataframes, subfolder, topics, years):
    i = 0
    for topic in topics:
        for year in years:
            dataframes[i].to_csv(f'data/{subfolder}/{topic}_{year}.csv')
            i += 1


def save_days_to_csv(dataframes, subfolder, topics, years):
    i = 0
    for topic in topics:
        for year in years:
            for month in range(1,13):
                dataframes[i].to_csv(f'data/{subfolder}/{topic}_{year}_{month}.csv')
                i += 1


'''
all availible topics are: access, login, rating, search, summary
    summary contains data from access, login and search
all availible years are: 2015 - 2020
'''

# url = 'https://susice.tritius.cz/statistics'

# topics = ['rating', 'summary']
# years = [i for i in range(2015, 2021)]
# dataframes_months = get_dataframes_months(url, topics, years)
# save_months_to_csv(dataframes_months, 'months', topics, years)

# # only data for 2019
# # daily ratings data is not interesting
# topics = ['access', 'login', 'search']
# years = [2019]
# dataframes_days = get_dataframes_days(url, topics, years)
# save_days_to_csv(dataframes_days, 'days', topics, years)
