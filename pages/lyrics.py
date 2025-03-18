import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__)

heading = dbc.Container('We got some information about tempo here')
main_content = dbc.Container('Some information about this project goes here. '
'This content answers questions about what data sources we used, how the data '
'was processed and what assumptions were made. Whilest this information not '
'being listed in the official requirements provided by CAU, it still holds a lot'
'of value from a scientific standpoint.')
screaming = dbc.Container('NEVER GONNA GIVE YOU UP, NEVER GONNA LET YOU DOWN, '
'NEVER GONNA RUN AROUND AND DESERT YOU. NEVER GONNA MAKE YOU CRY, NEVER GONNA '
'SAY GOODBYE, NEVER GONNA TELL A LIE AND HURT YOU!')

layout = html.Div([heading, main_content, screaming])