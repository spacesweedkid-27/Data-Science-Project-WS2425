import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Import Layout attributes to dynamically inject them into the page.
from pages.chords import layout as chords_layout
from pages.lyrics import layout as lyrics_layout
from pages.tempo import layout as tempo_layout

dash.register_page(__name__, path='/')

chord_data = pd.read_csv('data/chords_extracted/billboard_2005.csv')

# This page is basically a wrapper for chords, lyrics and tempo pages.
# There's really no need to change anything here.

###################################
# HTML / DBC ELEMENTS
###################################

heading = dbc.Container('On the development of popular music in the past two decades.',
    className='text-primary vw-10 h2 mb-2'
    )

introtext = dbc.Container([
    html.P('Music is a part of our culture that is not easily replaced. '
    'Music has been a way to communicate emotions for hundreds of years. Through '
    'music humans experience joy, sadness, love, grief - unity. Music has brought '
    'us together, continues to do so to this day. Yet everyone is different.'),
    html.P('Everyone is shaped by their own experiences, good and bad alike - they make '
    'up who we are, what we do and what we like. An individual\'s taste in music '
    'is no exception. Yet some songs find more popularity than others. We aim to '
    'find out why.')],
    class_name='mb-2'
    )


# Theme selection buttons. Would probably be far easier if we'd use a tab menu,
# but personally, especially in morph theme, I think these buttons look a lot
# better than the tab menu. 
button_row = dbc.Stack([
    dbc.Button('chords', color='primary', class_name='me-3', id='chords-trigger'),
    dbc.Button('lyrics', color='secondary', class_name='me-3', id='lyrics-trigger'),
    dbc.Button('tempo', color='danger', class_name='me-3', id='tempo-trigger')],
    class_name='d-grid gap-2 d-md-block mb-3 mx-auto', direction='horizontal')

# Defines position of dynamic page content within the home page.
# Will remain empty itself, as it's overwritten on init anyway. 
dynamic_container = dbc.Container([],id='dynamic-content')


# I think I was trying to understand, how finely grained you could work in dash
# in regards to structuring the site content. 
'''container = dbc.Container(
    [
        dbc.Row(
            dbc.Col(headings[0])
        ),
        dbc.Row(
            dbc.Col(misc_information[0])
        ),
        dbc.Row(
            dbc.Col(misc_information[1])
        ),
        dbc.Row(
            dbc.Col(button_row)
        )
    ],
    fluid=True,
    className='d-flex flex-wrap align-items-start align-items-center vw-100 justify-content-center mb-2')'''

###################################
# MAIN LAYOUT
###################################

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    #container,
    heading,
    introtext,
    button_row,
    dynamic_container
    #table
    ], class_name='mt-5 d-flex flex-wrap align-items-start align-items-center')

###################################
# CALLBACKS
###################################

@dash.callback(
    Output('dynamic-content', 'children'),
    [Input('chords-trigger', 'n_clicks'),
     Input('lyrics-trigger', 'n_clicks'),
     Input('tempo-trigger', 'n_clicks')]
)
def buttons_clicks(chords_clicks, lyrics_clicks, tempo_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return chords_layout
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'chords-trigger':
        return chords_layout
    elif button_id == 'lyrics-trigger':
        return lyrics_layout
    elif button_id == 'tempo-trigger':
        return tempo_layout