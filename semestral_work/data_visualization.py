import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

from bidict import bidict

import pandas as pd

import data_parsing as dapar

# UPDATE DATA ON EACH APP START
# url = 'https://susice.tritius.cz/statistics'

# topics = ['summary']
# years = [i for i in range(2015, 2021)]
# dataframes_months = dapar.get_dataframes_months(url, topics, years)
# dapar.save_months_to_csv(dataframes_months, 'months', topics, years)

# CONFIG AND HELPER VARIABLES
years = [year for year in range(2015, 2021)]

months = bidict({
    'Leden': 1,
    'Únor': 2,
    'Březen': 3,
    'Duben': 4,
    'Květen': 5,
    'Červen': 6,
    'Červenec': 7,
    'Srpen': 8,
    'Září': 9,
    'Říjen': 10,
    'Listopad': 11,
    'Prosinec': 12,
    'Souhrnně celkem': 13
})

init_year = 2020

# GLOBAL DATA
summary = {year: pd.read_csv(f'data/months/summary_{year}.csv', header=[0,1], index_col=0) for year in years}
rating = {year: pd.read_csv(f'data/months/rating_{year}.csv', header=[0,1], index_col=0) for year in years}

# DASH APP INIT
css = [dbc.themes.SUPERHERO]
app = dash.Dash(__name__, external_stylesheets=css)
app.title = 'Statistiky | Městská knihovna Sušice'

#######################################  LAYOUT  #######################################

# GRAPH TAB
tab_graph = html.Div([
    # GRAPH
    dcc.Graph(id='graph_summary', style={'margin': '30px 0 50px 0'}),
    # MONTH SLIDER
    html.Div([
        dcc.Slider(
            id='slider_month',
            min=1,
            max=13,
            step=None
        )
    ])
], style={'margin': '0 100px'})

# DATA TAB
tab_data = html.Div([
    dcc.Markdown('''### VYHLEDÁVÁNÍ - PŘÍSTUPY - PŘIHLAŠOVÁNÍ''', style={'text-align': 'center', 'margin': '25px'}),
    html.Div(id='table_summary'),

    dcc.Markdown('''### HODNOCENÍ''', style={'text-align': 'center', 'margin': '25px'}),
    html.Div(id='table_rating'),
])

# LAYOUT DESCRIPTION
app.layout = html.Div([
    html.Div(id='rating'),
    # YEAR PICKER
    dbc.FormGroup([
        dbc.Label('Rok'),
        dbc.RadioItems(
            options=[
                {'label': '2015', 'value': 2015},
                {'label': '2016', 'value': 2016},
                {'label': '2017', 'value': 2017},
                {'label': '2018', 'value': 2018},
                {'label': '2019', 'value': 2019},
                {'label': '2020', 'value': 2020}
            ],
            value=init_year,
            switch=True,
            inline=True,
            id='radio_year',
        ),
    ], style={'margin': '20px 0 0 0', 'textAlign': 'center'}),

    dbc.Tabs([
        dbc.Tab(tab_graph, label='Vizualizace', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#37b800'}),
        dbc.Tab(tab_data, label='Data', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#00AEF9'}),
    ]),
])

##################################  INTERACTIVITY  ##################################

# UPDATE SLIDER
@app.callback(
    [Output('slider_month', 'marks'),
    Output('slider_month', 'value')],
    [Input('radio_year', 'value')])
def update_slider(year):
    return {months[month]: month for month in summary[year].index.unique()}, months[summary[year].index.unique()[0]]


# UPDATE GRAPH
@app.callback(
    Output('graph_summary', 'figure'),
    [Input('radio_year', 'value'),
    Input('slider_month', 'value')])
def update_figure(year, month):
    df = summary[year]
    filt = df.loc[months.inverse[month]]
    # filt.loc['Vyhledávání'][0] is the same as filt.loc['Vyhledávání', 'V knihovně'] is the same as filt[0]
    # filt.loc['Přístupy'][2] is the same as filt.loc['Přístupy', 'Vše'] is the same as filt[5]
    data = [
        {
        'type': 'bar', 'name': 'V knihovně',
        'x': [df.columns[0][0], df.columns[3][0], df.columns[6][0]],
        'y': [filt.loc['Vyhledávání', 'V knihovně'], filt.loc['Přístupy', 'V knihovně'], filt.loc['Statistiky přihlášování', 'V knihovně']]
        },

        {
        'type': 'bar', 'name': 'Mimo knihovnu',
        'x': [df.columns[0][0], df.columns[3][0], df.columns[6][0]],
        'y': [filt.loc['Vyhledávání', 'Mimo knihovnu'], filt.loc['Přístupy', 'Mimo knihovnu'], filt.loc['Statistiky přihlášování', 'Mimo knihovnu']]
        },

        {
        'type': 'bar', 'name': 'Vše',
        'x': [df.columns[0][0], df.columns[3][0], df.columns[6][0]],
        'y': [filt.loc['Vyhledávání', 'Vše'], filt.loc['Přístupy', 'Vše'], filt.loc['Statistiky přihlášování', 'Vše']]
        },
    ]

    max_range = 5000
    changed = False
    if filt[2] > max_range or filt[5] > max_range or filt[8] > max_range:
        max_range = max(filt[2], filt[5], filt[8])
        changed = True

    return {
        'data': data,
        'layout': dict(
            xaxis={'linecolor': '2b3e50'},
            yaxis={'range': [0, max_range]},
            #margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
            legend={'x': 0, 'y': 1},
            transition = {'duration': 0 if changed else 500}, # ugly efect when rescaling y-axis
            height = 600,
            plot_bgcolor = '#2b3e50',
            paper_bgcolor = '#2b3e50',
            font = {'color': '#ffffff'}
        )
    }


# UPDATE DATA TABLE
@app.callback(
    [Output('table_summary', 'children'),
    Output('table_rating', 'children')],
    [Input('radio_year', 'value')])
def update_data(year):
    table_summary = dbc.Table.from_dataframe(summary[year], striped=True, borderless=True, index=True, responsive=True)
    table_rating = dbc.Table.from_dataframe(rating[year], striped=True, borderless=True, index=True, responsive=True)

    colors = {
        'V knihovně': '#1f77b4',
        'Mimo knihovnu': '#ff7f0e',
        'Vše': '#2ca02c'
    }

    # summary header repair
    head = html.Thead([
        html.Tr([
            html.Th('Měsíc'),
            html.Th(summary[year].columns[0][0], colSpan=3),
            html.Th(summary[year].columns[3][0], colSpan=3),
            html.Th(summary[year].columns[6][0], colSpan=3)
        ]),
        html.Tr(
            [html.Th('')] + [html.Th(col[1], style={'background': colors[col[1]]}) for col in summary[year]]
        )
    ])
    table_summary.children[0] = head

    # rating header repair
    head = html.Thead([
        html.Tr([
            html.Th('Měsíc'),
            html.Th(rating[year].columns[0][0], colSpan=3),
            html.Th(rating[year].columns[3][0], colSpan=3),
        ]),
        html.Tr(
            [html.Th('')] + [html.Th(col[1], style={'background': colors[col[1]]}) for col in rating[year]]
        )
    ])
    table_rating.children[0] = head

    return table_summary, table_rating


# UPDATE RATING
@app.callback(
    Output('rating', 'children'),
    [Input('radio_year', 'value'),
    Input('slider_month', 'value')])
def update_rating(year, month):
    df = rating[year]

    rating_contrib = df.loc[months.inverse[month], 'Hodnocení - příspěvky']['Vše']
    rating_stars = df.loc[months.inverse[month], 'Hodnocení - hvězdičky']['Vše']

    return html.Div([f'Příspěvky: {rating_contrib}']), html.Div([f'Hvězdičky: {rating_stars}'])

##################################  MAIN  ##################################

if __name__ == '__main__':
    app.run_server(debug=True)
