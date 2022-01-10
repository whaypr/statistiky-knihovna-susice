import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


# GLOBAL VARS
init_year = datetime.datetime.now().year

popup_message_path = os.path.join('app', 'assets', 'popup_message.md')
with open(popup_message_path) as f:
    popup_message = f.read()


# POPUP INFO
modal = html.Div([
    dbc.Modal([
            dbc.ModalBody(dcc.Markdown(popup_message)),
            dbc.ModalFooter(
                dbc.Button('Zavřít', id='close', className='ml-auto')
            ),
    ], id='modal', is_open=True, size='lg')
])


# YEAR PICKER
year_picker = dbc.FormGroup([
    dbc.RadioItems(
        options=[
            {'label': f'{year}', 'value': year}
            for year in range(2015, init_year + 1)
        ],
        value=init_year,
        switch=True,
        inline=True,
        id='radio_year',
    ),
], style={'margin': '25px 0', 'textAlign': 'center'})


# VISUALIZATION TAB
tab_graph = html.Div([
    # MONTH SLIDER
    dbc.Container([
        dcc.Slider(
            id='slider_month',
            min=1,
            max=13,
            step=None,
        )
    ], style={'margin': '30px auto'}),
    
    # GRAPHS
    dbc.Row([
        # GRAPH SUMMARY DAILY
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    dcc.Markdown('#### Celková denní data', style={'textAlign': 'center'}),
                ]),

                dbc.CardBody([
                    dcc.Graph(
                        id='graph_summary_daily',
                        config={
                            'displaylogo': False,
                            'modeBarButtonsToRemove': [
                                'select2d', 'lasso2d','zoomIn2d', 'zoomOut2d', 'resetScale2d', 'autoScale2d',
                                'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'
                            ],
                        },
                    )
                ])
            ], style={'background-color': '#2b3e50', 'border-color': '#3b4c5d', 'border-width': '4px'} )
        ], className='col-12 col-xl-8'),

        # GRAPH SUMMARY MONTHLY
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    dcc.Markdown('#### Celková měsíční data', style={'textAlign': 'center'}),
                ]),

                dbc.CardBody([
                    dcc.Graph(
                        id='graph_summary_monthly',
                        config={
                            'displaylogo': False,
                            'modeBarButtonsToRemove': [
                                'pan2d', 'select2d', 'lasso2d', 'zoom2d','zoomIn2d', 'zoomOut2d', 'resetScale2d',
                                'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'
                            ],
                        }
                    )
                ])
            ], style={'background-color': '#2b3e50', 'border-color': '#3b4c5d', 'border-width': '4px'})
        ], className='col-12 col-xl-4')
    ], style={'margin': '20px auto'}),

    # RATING NUMBERS
    html.Div(id='rating'),
])


# DATA TAB
tab_data = html.Div([
    # TITLE AND DONWLOAD LINKS
    html.Div([
        dcc.Markdown('''### VYHLEDÁVÁNÍ, PŘÍSTUPY, PŘIHLAŠOVÁNÍ'''),
        dbc.Row([
            # CSV LINK
            dbc.Col([
                html.A(
                    'Stáhnout roční data [CSV]', id='link_download_csv',
                    download='', href='', target='_blank'
                ),
            ]),
            
            # HTML LINK
            dbc.Col([
                html.A(
                    'Stáhnout roční data [HTML]', id='link_download_html',
                    download='', href='', target='_blank'
                ),
            ]),
        ]),   
    ], style={'text-align': 'center', 'margin': '25px'}),

    # TABLE SUMMARY
    html.Div(id='table_summary'),

    # TITLE AND TABLE RATINGS
    dcc.Markdown('''### HODNOCENÍ''', style={'text-align': 'center', 'margin': '25px'}),
    html.Div(id='table_rating'),
])


# LAYOUT DESCRIPTION
def make_layout():
    return html.Div([
        # STORES PAGE WIDTH
        html.Div(id='size', style={'display': 'none'}), dcc.Location(id='url'),
        # POPUP INFO
        modal,
        # YEAR PICKER
        year_picker,
        # TABS
        dbc.Tabs([
            dbc.Tab(tab_graph, label='Vizualizace', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#37b800'}),
            dbc.Tab(tab_data, label='Data', tab_style={'width': '200px', 'textAlign': 'center', 'margin': 'auto'}, label_style={'color': '#00AEF9'}),
        ]),
    ])
