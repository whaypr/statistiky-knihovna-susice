from data import update_library_data

from concurrent.futures import ThreadPoolExecutor

import dash
import dash_bootstrap_components as dbc


# DASH APP INIT
css = [dbc.themes.SUPERHERO]
meta_tags=[
    {'name': 'viewport', 'content': 'width=device-width, user-scalable=no'},

    {'property': 'og:image', 'content': 'https://statistiky-knihovna-susice.herokuapp.com/assets/thumbnail.png'},
    {'property': 'og:image:type', 'content': 'image/png'},
    {'property': 'og:image:width', 'content': '1920'},
    {'property': 'og:image:height', 'content': '920'}
]

app = dash.Dash(__name__, external_stylesheets=css, meta_tags=meta_tags)

app.title = 'Statistiky | Městská knihovna Sušice'
app.layout = make_layout

server = app.server # for gunicorn

# RUN DATA UPDATE FUNC IN ANOTHER THREAD 
executor = ThreadPoolExecutor(max_workers=1)
executor.submit(update_library_data)