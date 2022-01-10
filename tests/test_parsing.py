import pytest
from pandas.testing import assert_frame_equal

import os
import pandas as pd

import app.parsing as datpar


### PARSED DATA TESTING
### test values in csv files with values from the web

def test_data_months_summary():
    path = os.path.join('data', 'months', 'summary_2019.csv')
    summary_2019 = pd.read_csv(path, header=[0,1], index_col=0)

    assert summary_2019.loc['Květen', 'Vyhledávání']['V knihovně'] == 121
    assert summary_2019.loc['Květen', 'Vyhledávání']['Mimo knihovnu'] == 2232
    assert summary_2019.loc['Květen', 'Vyhledávání']['Vše'] == 2353

    assert summary_2019.loc['Prosinec', 'Přístupy']['V knihovně'] == 36
    assert summary_2019.loc['Prosinec', 'Přístupy']['Mimo knihovnu'] == 613
    assert summary_2019.loc['Prosinec', 'Přístupy']['Vše'] == 649

    assert summary_2019.loc['Souhrnně celkem', 'Statistiky přihlášování']['V knihovně'] == 26
    assert summary_2019.loc['Souhrnně celkem', 'Statistiky přihlášování']['Mimo knihovnu'] == 4437
    assert summary_2019.loc['Souhrnně celkem', 'Statistiky přihlášování']['Vše'] == 4463

    path = os.path.join('data', 'months', 'summary_2015.csv')
    summary_2015 = pd.read_csv(path, header=[0,1], index_col=0)

    with pytest.raises(KeyError):
        summary_2015.loc['Únor']
    with pytest.raises(KeyError):
        summary_2015.loc['Říjen']


def test_data_months_rating():
    path = os.path.join('data', 'months', 'rating_2019.csv')
    rating_2019 = pd.read_csv(path, header=[0,1], index_col=0)

    assert rating_2019.loc['Červenec', 'Hodnocení - příspěvky']['V knihovně'] == 0
    assert rating_2019.loc['Červenec', 'Hodnocení - příspěvky']['Mimo knihovnu'] == 1
    assert rating_2019.loc['Červenec', 'Hodnocení - příspěvky']['Vše'] == 1

    assert rating_2019.loc['Souhrnně celkem', 'Hodnocení - hvězdičky']['V knihovně'] == 0
    assert rating_2019.loc['Souhrnně celkem', 'Hodnocení - hvězdičky']['Mimo knihovnu'] == 0
    assert rating_2019.loc['Souhrnně celkem', 'Hodnocení - hvězdičky']['Vše'] == 0

    path = os.path.join('data', 'months', 'rating_2020.csv')
    rating_2020 = pd.read_csv(path, header=[0,1], index_col=0)

    with pytest.raises(KeyError):
        rating_2020.loc['Prosinec']


def test_data_days_access():
    path = os.path.join('data', 'days', '2019', 'access_2019_5.csv')
    access_2019_5 = pd.read_csv(path, index_col=0)

    assert len(access_2019_5.index) == 31
    assert access_2019_5.loc[1, 'Počet'] == 21
    assert access_2019_5.loc[31, 'Počet'] == 31
    with pytest.raises(KeyError):
        access_2019_5.loc[0]
    with pytest.raises(KeyError):
        access_2019_5.loc[32]


def test_data_days_login():
    path = os.path.join('data', 'days', '2020', 'login_2020_2.csv')
    login_2020_2 = pd.read_csv(path, index_col=0)

    assert len(login_2020_2.index) == 29
    assert login_2020_2.loc[8, 'Počet'] == 4
    assert login_2020_2.loc[19, 'Počet'] == 30
    with pytest.raises(KeyError):
        login_2020_2.loc[0]
    with pytest.raises(KeyError):
        login_2020_2.loc[30]


def test_data_days_search():
    path = os.path.join('data', 'days', '2016', 'search_2016_7.csv')
    search_2016_7 = pd.read_csv(path, index_col=0)

    assert len(search_2016_7.index) == 31
    assert search_2016_7.loc[12, 'Počet'] == 97 + 31 + 5
    assert search_2016_7.loc[24, 'Počet'] == 25 + 6
    with pytest.raises(KeyError):
        search_2016_7.loc[0]
    with pytest.raises(KeyError):
        search_2016_7.loc[32]


### PARSING DATA TESTING

def test_parsing_months():
    url = 'https://susice.tritius.cz/statistics'

    years = [i for i in range(2015, 2021)]
    topics = ['rating']
    dataframes_months = datpar.get_dataframes_months(url, topics, years)

    assert len(dataframes_months) == 6

    years = [i for i in range(2018, 2020)]
    topics = ['rating', 'access']
    dataframes_months = datpar.get_dataframes_months(url, topics, years)

    assert len(dataframes_months) == 4
    