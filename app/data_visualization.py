import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd

import os
from bidict import bidict
import urllib


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


# DASH APP INIT
css = [dbc.themes.SUPERHERO]
app = dash.Dash(__name__, external_stylesheets=css)
app.title = 'Statistiky | Městská knihovna Sušice'

#############################################################################################################################################################
##  L A Y O U T  ########  L A Y O U T  ########  L A Y O U T  ########  L A Y O U T  ########  L A Y O U T  ########  L A Y O U T  ########  L A Y O U T  ##
#############################################################################################################################################################

# VISUALIZATION TAB
tab_graph = html.Div([
    # GRAPHS
    html.Div([
        # GRAPH SUMMARY DAILY
        html.Div([
            dcc.Markdown('#### Celková denní data', style={'textAlign': 'center'}),
            dcc.Graph(id='graph_summary_daily')
        ], className='col-8'),
        # GRAPH SUMMARY MONTHLY
        html.Div([
            dcc.Markdown('#### Celková měsíční data', style={'textAlign': 'center'}),
            dcc.Graph(id='graph_summary_monthly')
        ], className='col-4')
    ], className='row', style={'margin': '20px 0 0 0'}),

    # RATING NUMBERS
    html.Div(id='rating'),

    # MONTH SLIDER
    html.Div([
        dcc.Slider(
            id='slider_month',
            min=1,
            max=13,
            step=None,
        )
    ], style={'margin': '30px 200px 0 200px'}),
])


# DATA TAB
tab_data = html.Div([
    # TITLE AND DONWLOAD LINKS
    html.Div([
        dcc.Markdown('''### VYHLEDÁVÁNÍ - PŘÍSTUPY - PŘIHLAŠOVÁNÍ'''),
        # CSV
        html.A(
            'Stáhnout roční data v CSV formátu', id='link_download_csv',
            download='', href='', target='_blank',
            style={'margin': 'auto 50px auto 0'}
        ),
        # HTML
        html.A(
            'Stáhnout roční data v HTML formátu', id='link_download_html',
            download='', href='', target='_blank',
            style={'margin': 'auto'}
        ),
    ], style={'text-align': 'center', 'margin': '25px'}),
    # TABLE
    html.Div(id='table_summary'),

    dcc.Markdown('''### HODNOCENÍ''', style={'text-align': 'center', 'margin': '25px'}),
    html.Div(id='table_rating'),
])


# LAYOUT DESCRIPTION
app.layout = html.Div([
    # YEAR PICKER
    dbc.FormGroup([
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
    # TABS
    dbc.Tabs([
        dbc.Tab(tab_graph, label='Vizualizace', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#37b800'}),
        dbc.Tab(tab_data, label='Data', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#00AEF9'}),
    ]),
])

#############################################################################################################################################################
##  I N T E R A C T I V I T Y  ############  I N T E R A C T I V I T Y  #############  I N T E R A C T I V I T Y  ############  I N T E R A C T I V I T Y  ##
#############################################################################################################################################################

# UPDATE SLIDER
@app.callback(
    [Output('slider_month', 'marks'),
    Output('slider_month', 'value')],
    [Input('radio_year', 'value')])
def update_slider(year):
    return (
        {months[month]: {'label': month, 'style': {'color': '#ffffff', 'fontSize': '1.1em'}} for month in summary[year].index.unique()},
        months[summary[year].index.unique()[0]]
    )


# UPDATE GRAPH SUMMARY DAILY
@app.callback(
    Output('graph_summary_daily', 'figure'),
    [Input('radio_year', 'value'),
    Input('slider_month', 'value')])
def update_figure_daily(year, month):
    # 13. month is data for whole year, which is not availible for concrete days
    # so we set month and year on January 2015 which is all zeroes
    if month == 13:
        year = 2015
        month = 1

    acc = access[f'{year}:{month}']
    log = login[f'{year}:{month}']
    ser = search[f'{year}:{month}']

    data = [
        {
        'type': 'bar', 'name': 'Vyhledávání',
        'x': [f'{day}' for day in ser.index],
        'y': [ser.loc[day][0] for day in ser.index]
        },

        {
        'type': 'bar', 'name': 'Přístupy',
        'x': [f'{day}' for day in acc.index],
        'y': [acc.loc[day][0] for day in acc.index]
        },

        {
        'type': 'bar', 'name': 'Přihlášení',
        'x': [f'{day}' for day in log.index],
        'y': [log.loc[day][0] for day in log.index]
        },
    ]

    return {
        'data': data,
        'layout': dict(
            xaxis={'linecolor': '2b3e50', 'tickmode': 'linear'},
            yaxis={'range': [0, 200]},
            #margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
            legend={'xanchor':'center', 'yanchor':'top', 'y':1.3, 'x':0.5 },
            transition={'duration': 500}, # ugly efect when rescaling axis
            height=600,
            plot_bgcolor='#2b3e50',
            paper_bgcolor='#2b3e50',
            font={'color': '#ffffff'},
        )   
    }


# UPDATE GRAPH SUMMARY MONTHLY
@app.callback(
    Output('graph_summary_monthly', 'figure'),
    [Input('radio_year', 'value'),
    Input('slider_month', 'value')])
def update_figure_monthly(year, month):
    df = summary[year]
    filt = df.loc[months.inverse[month]]

    # filt.loc['Vyhledávání'][0] is the same as filt.loc['Vyhledávání', 'V knihovně'] is the same as filt[0]
    # filt.loc['Přístupy'][2] is the same as filt.loc['Přístupy', 'Vše'] is the same as filt[5]
    search = [filt.loc['Vyhledávání', 'V knihovně'], filt.loc['Vyhledávání', 'Mimo knihovnu'], filt.loc['Vyhledávání', 'Vše']]
    access = [filt.loc['Přístupy', 'V knihovně'], filt.loc['Přístupy', 'Mimo knihovnu'], filt.loc['Přístupy', 'Vše']]
    login = [filt.loc['Statistiky přihlášování', 'V knihovně'], filt.loc['Statistiky přihlášování', 'Mimo knihovnu'], filt.loc['Statistiky přihlášování', 'Vše']]
    data = [
        {
        'type': 'bar', 'name': 'Vyhledávání',
        'y': [df.columns[0][1], df.columns[1][1], df.columns[2][1]],
        'x': search,
        'orientation': 'h', 'hoverinfo':'skip',
        'text': search, 'textposition': 'outside'
        },

        {
        'type': 'bar', 'name': 'Přístupy',
        'y': [df.columns[0][1], df.columns[1][1], df.columns[2][1]],
        'x': access,
        'orientation': 'h', 'hoverinfo':'skip',
        'text': access, 'textposition': 'outside'
        },

        {
        'type': 'bar', 'name': 'Přihlášení',
        'y': [df.columns[0][1], df.columns[1][1], df.columns[2][1]],
        'x': login,
        'orientation': 'h', 'hoverinfo':'skip',
        'text': login, 'textposition': 'outside'
        }
    ]

    max_range = 4500
    changed = False
    if filt[2] > max_range or filt[5] > max_range or filt[8] > max_range:
        max_range = max(filt[2], filt[5], filt[8])
        changed = True

    return {
        'data': data,
        'layout': dict(
            yaxis={'linecolor': '2b3e50'},
            xaxis={'range': [0, max_range]},
            margin={'l': 90},
            legend={'xanchor':'center', 'yanchor':'top', 'y':1.2, 'x':0.5 },
            transition={'duration': 0 if changed else 500}, # ugly efect when rescaling axis
            height=600,
            plot_bgcolor='#2b3e50',
            paper_bgcolor='#2b3e50',
            font={'color': '#ffffff'},
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
        'Vyhledávání': '#1f77b4',
        'Přístupy': '#ff7f0e',
        'Přihlášení': '#2ca02c',
        'header': '#1a2631'
    }

    # summary header repair
    head = html.Thead([
        html.Tr([
            html.Th('Měsíc'),
            html.Th(summary[year].columns[0][0], colSpan=3, style={'background': colors['Vyhledávání']}),
            html.Th(summary[year].columns[3][0], colSpan=3, style={'background': colors['Přístupy']}),
            html.Th(summary[year].columns[6][0], colSpan=3, style={'background': colors['Přihlášení']})
        ]),
        html.Tr(
            [html.Th('', style={'background': colors['header']})] + [html.Th(col[1], style={'background': colors['header']}) for col in summary[year]]
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
            [html.Th('', style={'background': colors['header']})] + [html.Th(col[1], style={'background': colors['header']}) for col in rating[year]]
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

    return (
        html.Div(f'Hodnocení - příspěvky: {rating_contrib}', style={'textAlign': 'center'}), 
        html.Div(f'Hodnocení - hvězdičky: {rating_stars}', style={'textAlign': 'center'})   
    )


# UPDATE DOWNLOAD CSV LINK
@app.callback(
    [Output('link_download_csv', 'download'),
    Output('link_download_csv', 'href')],
    [Input('radio_year', 'value'),
    Input('slider_month', 'value')])
def update_download_link_csv(year, month):
    filt = summary[year]
    csv_string = filt.to_csv(index=True, encoding='utf-8')
    csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)

    return f'summary_{year}.csv', csv_string


# UPDATE DOWNLOAD HTML LINK
@app.callback(
    [Output('link_download_html', 'download'),
    Output('link_download_html', 'href')],
    [Input('radio_year', 'value'),
    Input('slider_month', 'value')])
def update_download_link_html(year, month):
    filt = summary[year]
    html_string = filt.to_html(index=True)
    html_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(html_string)

    return f'summary_{year}.html', html_string

#############################################################################################################################################################
###  M A I N  #################  M A I N  #################  M A I N  #################  M A I N  #################  M A I N  #################  M A I N  ###
#############################################################################################################################################################

if __name__ == '__main__':
    app.run_server()
