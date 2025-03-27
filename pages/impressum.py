# Dash related imports
import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__)

content = dbc.Container([
    html.H3('Impressum'),
    html.P('''This website is hosted as part of a student project at Christian-
           Albrechts-Universität zu Kiel.\n
           Information according to §5 TMG:'''),
    html.Ul([
        html.Li('Nike Pulow'),
        html.Li('Hansaring 127'),
        html.Li('24534 Neumünster'),
        html.Li('stu239549@mail.uni-kiel.de')
    ])
])

layout = html.Div(content)