import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
import os


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
    # includes links to nonexisting data -> resulting dataframes are filled with zeroes
    links = [f'{url}/{topic}/{year}/{month}' for topic in topics for year in years for month in range(1,13)]

    # loop through all links and parse data from them into dataframes
    dataframes_days = []
    for link in links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        text = str(soup.find_all('script')[3])
        pattern = re.compile('var totalChartData = (.*?);')
        match = pattern.search(text)
        data = json.loads(match.groups()[0].replace('\'', '"').replace('\\', '')) # replaces are for removing invalid json parts

        # all data parts are summed together
        res = []
        for i in range(len(data['datasets'][0]['data'])):
            val = 0
            for j in range(len(data['datasets'])):
                val += data['datasets'][j]['data'][i]
            res.append(val)

        data = enumerate(res, start=1)

        df = pd.DataFrame(data, columns=['Den', 'Počet']) 
        df.set_index('Den', inplace=True)

        dataframes_days.append(df)

    return dataframes_days


def save_months_to_csv(dataframes, subfolder, topics, years):
    # create file structure if not exists
    path = os.path.join('data', subfolder)
    if not os.path.exists(path):
        os.makedirs(path)

    i = 0
    for topic in topics:
        for year in years:
            path = os.path.join('data', subfolder, f'{topic}_{year}.csv')
            dataframes[i].to_csv(path)
            i += 1


def save_days_to_csv(dataframes, subfolder, topics, years):
    # create file structure if not exists
    paths = [os.path.join('data', subfolder, str(year)) for year in years]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)

    i = 0
    for topic in topics:
        for year in years:
            for month in range(1,13):
                path = os.path.join('data', subfolder, str(year), f'{topic}_{year}_{month}.csv')
                dataframes[i].to_csv(path)
                i += 1


# parse data only when called as script
if __name__ == "__main__":
    '''
    all availible topics are: access, login, rating, search, summary
        summary contains data from access, login and search
    all availible years are: 2015 - 2020
    '''

    url = 'https://susice.tritius.cz/statistics'
    years = [i for i in range(2015, 2021)]

    topics = ['rating', 'summary']
    dataframes_months = get_dataframes_months(url, topics, years)
    save_months_to_csv(dataframes_months, 'months', topics, years)

    topics = ['access', 'login', 'search']
    dataframes_days = get_dataframes_days(url, topics, years)
    save_days_to_csv(dataframes_days, 'days/', topics, years)
