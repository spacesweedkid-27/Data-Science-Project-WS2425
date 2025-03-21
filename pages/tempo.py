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
# GRAPH TEMPLATE pt.1
###################################

# Here goes everything needed to create the graph such as data imports, 
# functions and other logic not related to the actual output object.

# Naming conventions:
# functions related to generation of the figure:            create_xaxis_yaxis_figtype()
#                                                           update_xaxis_yaxis_figtype()
#                                                           (or whatever else applies)
# temporary objects / interim results:                      xaxis_yaxis_figtype_tempdescriptor
# initialization object:                                    init_xaxis_yaxis_figtype
# (with tempdescriptor meaning a combination of words best
# describing the result of the interim / temporary object)

# We always need a create_function that receives the theme
# as a parameter. This is necessary for theme-changes.
# You don't necessarily need to use the plotly grpahic object (go) package.
# Plotly express (px) is fine as well. Just be aware, that the wrapper should
# remain a go.Figure for consistency.
'''
def create_xaxis_yaxis_figtype(theme):
    xaxis_yaxis_figtype = go.Figure(data = go.Figuretype(
        x = ...,
        y = ...,
        z = ...,
        ...
    )
    
    xaxis_yaxis_figtype.update_layout(
        # axis titles and so on
        autosize = True,
        height = 600, #  Can be changed to different value when it makes sense
        template = theme,
    )
    return xaxis_yaxis_figtype)
'''

# We always need to initialize the object once on load by using
# the create function. 
'''
init_xaxis_yaxis_figtype = create_xaxis_yaxis_figtype(theme)
'''

###################################
# HTML ELEMENTS
###################################

# Define your html elements such as dbc.Container or dbc.Sliders here.
# Any related callbacks need to be defined in app.py
# Name these elements precisely and plug them into the layout below.

###################################
# GRAPH TEMPLATE pt.2
###################################

# Naming conventions:
# for the actual figure that will be put into the layout:   xaixs_yaxis_figtype
# corresponding id:                                         xaxis-yaxis-figtype
# variable that holds slider / filter options:              xaxis_yaxis_figtype_slider
# corresponding id:                                         xaxis-yaxis-figtype-slider

# The actual HTML element for the graphic will be created here:
'''
xaxis_yaxis_figtype = dbc.Container([
    html.H3('Title'),
    <name of slider / filter toggle python object if it exists>,
    dcc.Graph(
        id = 'xaxis-yaxis-figtype',
        figure = init_xaxis_yaxis_figtype
    ), class_name = 'mt-3'
])
'''

# Interactive sliders / toggles / filters are defined here.
# Find out, what might be useful, look up documentation on how to create it.
# Important is, that the id corresponds to the naming conventions and accurately
# names what type of toggle / switch / whatever is used. This way, when looking
# through the callbacks in app.py it is easy to recognize what elements belong
# to which figure. The identification of where errors come from is also easier
# this way.
'''
xaxis_yaxis_figtype_slider = dcc.Slider(
    id = 'xaxis-yaxis-figtype-slider'
    ...
    )
'''

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
                   '''
                   xaxis_yaxis_figtype,
                   '''
                   ])