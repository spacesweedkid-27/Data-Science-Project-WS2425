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
questions = dbc.Container([
    'How do various musical elements vary in the most popular songs of the last '
    'twenty years?',
    html.Ul([
        html.Li([
            html.Strong('Chords, harmony and progressions:'),
            html.Ul([
                html.Li('What chord-progressions repeat most frequently?'),
                html.Li('What chords and chord types dominate?'),
                html.Li('How did the amount of chords change?'),
                html.Li('Do certain chord-progressions dominate specific genres?'),
                html.Li('What key signatures dominate?')
            ])
        ]),
        html.Li([
            html.Strong('Time'),
            html.Ul([
                html.Li('How did song duration vary and change over the years?'),
                html.Li('How does song tempo vary and change over the years?'),
                html.Li('Do these characteristics correlate to other examined aspects?')
            ])
        ]),
        html.Li([
            html.Strong('Lyrics'),
            html.Ul([
                html.Li('How does the polarity of lyrics vary and chagne over the years?'),
                html.Li('Which words and phrases are the most frequent?')
            ])
        ])
    ])
], class_name='mb-2')


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

challenges_heading = dbc.Container('challenges', class_name='h3 mt-4')
challenges = dbc.Container('TODO: Description on what challenges we faced.')

layout = html.Div([
    about_heading,
    introduction,
    questions_heading,
    questions,
    datasources_heading,
    datasources,
    challenges_heading,
    challenges
    ])