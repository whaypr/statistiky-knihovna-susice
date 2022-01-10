from data import summary, rating, access, login, search
from app import app

import urllib

import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


# GLOBAL VARS
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

width_breakpoint = 1000


# GET PAGE WIDTH
app.clientside_callback(
    '''
    function(largeValue1) {
        return window.innerWidth
    }
    ''',
    Output('size', 'children'),
    [Input('url', 'href')]
)


# POPUP CLOSE BUTTON
@app.callback(
    Output('modal', 'is_open'),
    [Input('close', 'n_clicks')]
)
def toggle_modal(n):
    return False if n else True


# UPDATE SLIDER
@app.callback(
    [Output('slider_month', 'marks'),
    Output('slider_month', 'value')],
    [Input('radio_year', 'value'),
    Input('size', 'children')])
def update_slider(year, width):
    month_slice = slice(0, 3) if int(width) < width_breakpoint else slice(0, None)
    rotation = 'translateX(-25px) translateY(10px) rotate(-45deg)' if int(width) < width_breakpoint else 'rotate(0deg) translateX(-15px)'

    return (
        {
            months[month]: 
            {
                'label': month[month_slice] if month != 'Souhrnně celkem' else 'Souhrnně',
                'style': {'color': '#ffffff' if month != 'Souhrnně celkem' else '#2ca02c', 'fontSize': '1.15em', 'transform': rotation}
            }
            for month in summary[year].index.unique()
        },

        months[summary[year].index.unique()[0]]
    )


# UPDATE GRAPH SUMMARY DAILY
@app.callback(
    Output('graph_summary_daily', 'figure'),
    [Input('radio_year', 'value'),
    Input('slider_month', 'value'),
    Input('size', 'children')])
def update_figure_daily(year, month, width):
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
        'x': [f'{day}' for day in range(1,32)],
        'y': [ser.loc[day][0] if day <= len(ser.index) else 0 for day in range(1,32)]
        },

        {
        'type': 'bar', 'name': 'Přístupy',
        'x': [f'{day}' for day in range(1,32)],
        'y': [acc.loc[day][0] if day <= len(acc.index) else 0 for day in range(1,32)]
        },

        {
        'type': 'bar', 'name': 'Přihlášení',
        'x': [f'{day}' for day in range(1,32)],
        'y': [log.loc[day][0] if day <= len(log.index) else 0 for day in range(1,32)]
        },
    ]

    graph_columns = 10 if int(width) < width_breakpoint else 31
    graph_height = 400 if int(width) < width_breakpoint else 600

    return {
        'data': data,
        'layout': dict(
            xaxis={'range': [0, graph_columns], 'linecolor': '2b3e50', 'tickmode': 'linear'},
            yaxis={'range': [0, 200]},
            margin={'l': 30, 'b': 25, 't': 0, 'r': 10, 'pad': 0},
            legend={'xanchor': 'center', 'yanchor': 'top', 'y': 1.3, 'x': 0.5 },
            transition={'duration': 500}, # ugly efect when rescaling axis
            height=graph_height,
            plot_bgcolor='#2b3e50',
            paper_bgcolor='#2b3e50',
            font={'color': '#ffffff'},
            dragmode='orbit',
        )   
    }


# UPDATE GRAPH SUMMARY MONTHLY
@app.callback(
    Output('graph_summary_monthly', 'figure'),
    [Input('radio_year', 'value'),
    Input('slider_month', 'value'),
    Input('size', 'children')])
def update_figure_monthly(year, month, width):
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
        max_range = max(filt[2], filt[5], filt[8]) * 1.1 # 1.1 for labels to be visible
        changed = True

    graph_height = 400 if int(width) < width_breakpoint else 600

    return {
        'data': data,
        'layout': dict(
            yaxis={'linecolor': '2b3e50'},
            xaxis={'range': [0, max_range]},
            margin={'l': 85, 'b': 0, 't': 0, 'r': 0, 'pad': 0},
            legend={'xanchor':'center', 'yanchor':'top', 'y':1.2, 'x':0.25 },
            transition={'duration': 0 if changed else 500}, # ugly efect when rescaling axis
            height=graph_height,
            plot_bgcolor='#2b3e50',
            paper_bgcolor='#2b3e50',
            font={'color': '#ffffff'},
            dragmode=False
        )
    }


# UPDATE DATA TABLE
@app.callback(
    [Output('table_summary', 'children'),
    Output('table_rating', 'children')],
    [Input('radio_year', 'value')])
def update_tables(year):
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
