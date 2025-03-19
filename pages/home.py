import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


from pages.chords import layout as chords_layout
from pages.lyrics import layout as lyrics_layout
from pages.tempo import layout as tempo_layout

dash.register_page(__name__, path='/')

chord_data = pd.read_csv('data/chords_extracted/billboard_2005.csv')

###################################

# html here
'''app.layout = dbc.Alert(
    "wip! Let's see.", className="m-5"
)'''
headings = [
    dbc.Container('informational information about music, yaya', className='text-primary vw-10 h2 mb-2')
]

misc_information = [
    dbc.Container('This text contains information, just so you know. '
    'Let me tell you why Lateralus by Tool is such a masterpiece. I\'m not '
    'really in the mood to type it out right now, but ya\'ll better believe '
    'me, fr.', class_name='mb-2'),
    dbc.Container('This is another block of information. We can write anything here, '
    'but I think some basic information about what we\'re looking at would be '
    'good - to get people into the groove, so to speak.', class_name='mb-2')
]

button_row = dbc.Stack([
    dbc.Button('chords', color='primary', class_name='me-3', id='chords-trigger'),
    dbc.Button('lyrics', color='secondary', class_name='me-3', id='lyrics-trigger'),
    dbc.Button('tempo', color='danger', class_name='me-3', id='tempo-trigger')],
    class_name='d-grid gap-2 d-md-block mb-3')

#table = dbc.Table.from_dataframe(chord_data, striped=True, bordered=True, hover=True, id='dynamic-content')
dynamic_container = dbc.Container([],id='dynamic-content')

container = dbc.Container(
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
    className='d-flex flex-wrap align-items-start align-items-center vw-100 justify-content-center mb-2')

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    container,
    dynamic_container
    #table
    ])

###################################
# Callbacks
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