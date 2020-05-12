import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

from bidict import bidict

import pandas as pd

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
dataframes = {year: pd.read_csv(f'data/months/summary_{year}.csv', header=[0,1], index_col=0) for year in years}

# DASH APP INIT
css = [dbc.themes.SUPERHERO]
app = dash.Dash(__name__, external_stylesheets=css)

############################  LAYOUT  ############################

# GRAPH TAB
tab_graph = html.Div([
    # GRAPH
    dcc.Graph(id='graph', style={'margin': '30px 0 50px 0'}),
    # MONTH SLIDER
    html.Div([
        dcc.Slider(
            id='month-slider',
            min=1,
            max=13,
            step=None
        )
    ])
], style={'margin': '0 100px'})

# DATA TAB
tab_data = html.Div(id='data-table', style={'margin': '20px'})

# LAYOUT DESCRIPTION
app.layout = html.Div([
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
            id='year-input',
        ),
    ], style={'margin': '20px 0 0 0', 'textAlign': 'center'}),

    dbc.Tabs([
        dbc.Tab(tab_graph, label='Vizualizace', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#37b800'}),
        dbc.Tab(tab_data, label='Data', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#00AEF9'}),
    ]),
])

############################  INTERACTIVITY  ############################

# UPDATE SLIDER
@app.callback(
    [Output('month-slider', 'marks'),
    Output('month-slider', 'value')],
    [Input('year-input', 'value')])
def update_slider(year):
    return {months[month]: month for month in dataframes[year].index.unique()}, months[dataframes[year].index.unique()[0]]


# UPDATE GRAPH
@app.callback(
    Output('graph', 'figure'),
    [Input('year-input', 'value'),
    Input('month-slider', 'value')])
def update_figure(year, month):
    df = dataframes[year]
    filt = df.loc[months.inverse[month]]
    data = [
        {'x': [df.columns[0][0], df.columns[3][0], df.columns[6][0]], 'y': [filt[0], filt[3], filt[6]], 'type': 'bar', 'name': 'V knihovně'},
        {'x': [df.columns[0][0], df.columns[3][0], df.columns[6][0]], 'y': [filt[1], filt[4], filt[7]], 'type': 'bar', 'name': 'Mimo knihovnu'},
        {'x': [df.columns[0][0], df.columns[3][0], df.columns[6][0]], 'y': [filt[2], filt[5], filt[8]], 'type': 'bar', 'name': 'Vše'},
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
    Output('data-table', 'children'),
    [Input('year-input', 'value')])
def update_slider(year):
    table = dbc.Table.from_dataframe(dataframes[year], striped=True, hover=True, bordered=True, index=True)

    # need to repair header due to the bad styling
    head = html.Thead([
        html.Tr([
            html.Th('Měsíc'),
            html.Th(dataframes[year].columns[0][0], colSpan=3),
            html.Th(dataframes[year].columns[3][0], colSpan=3),
            html.Th(dataframes[year].columns[6][0], colSpan=3)
        ]),
        html.Tr(
            [html.Th('')] + [html.Th(col[1]) for col in dataframes[year]]
        )
    ])
    
    table.children[0] = head

    return table

############################  MAIN  ############################

if __name__ == '__main__':
    app.run_server(debug=True)
