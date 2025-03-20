import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__)

about_heading = dbc.Container('About this project', class_name='h2 mt-5')
introduction = dbc.Container('This website is part of a university research '
'project analyzing trends in popular music over the past two decades. It was '
'conducted by a group of computer science students. Our research questions focus '
'on identifying patterns in musical composition, lyrical themes, and genre '
'evolution from 2005 to 2024.', class_name='mb-2')
questions_heading = dbc.Container('the questions', class_name='h3 mt-4')
questions = dbc.Container('The questions go here.', class_name='mb-2')
datasources_heading = dbc.Container('datasources', class_name='h3 mt-4')
datasources = dbc.Container(
    ['To explore these questions, we gathered data from multiple sources: ',
        html.Ul([
            html.Li([
                html.Strong('Billboard Year-End Hot 100 (2005-2024): '),
                'provided the top 100 most commercially successful songs each year.'
            ], className='mb-2'),
            html.Li([
                html.Strong('Ultimate Guitar: '),
                'used to retrieve chords progressions. Some songs were unavailable '
                'due to licensing issues.'
            ], className='mb-2'),
            html.Li([
                html.Strong('songbpm.com: '),
                'provided tempo (beats per minute) data.'
            ], className='mb-2'),
            html.Li([
                html.Strong('Genius API: '),
                'used to collect lyrics for textual and thematic analysis.'
            ], className='mb-2'),
            html.Li([
                html.Strong('last.fm API: '),
                'extracted genre classifications using top user-generated tags.'
            ], className='mb-2')
        ], className='mt-3')
    ]
)

layout = html.Div([
    about_heading,
    introduction,
    questions_heading,
    questions,
    datasources_heading,
    datasources
    ])