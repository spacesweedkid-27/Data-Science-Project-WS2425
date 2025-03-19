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

###################################
# GRAPHS
###################################

# Import or define your graphs here.
# Create one section (### #TITLE ###) for each graph. This makes it easier
# to look for certain elements. Try to keep naming precise.

###################################
# HTML ELEMENTS
###################################

# Define your html elements such as dbc.Container or dbc.Sliders here.
# Any related callbacks need to be defined in app.py
# Name these elements precicesly and plugg them into the layout below.

###################################
# MAIN LAYOUT
###################################

# Layout elements can be plugged in here.
# Don't change the name from layout to anything else. Dash page
# registry needs this attribute to properly load the content.
layout = html.Div([heading,
                   main_content,
                   # More html / dbc Elements can be added here
                   # in the preferred order. Don't forget the commas.
                   ])