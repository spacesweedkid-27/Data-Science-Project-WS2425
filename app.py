'''
DS Project Website
Für Fortnite
'''

import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc

app = Dash(__name__,
    external_stylesheets=[dbc.themes.MORPH, dbc.icons.FONT_AWESOME],
    use_pages=True
)
server=app.server

###################################
# data imports go here
###################################
# Should probably load data within pages, so data gets rendered on view, not on
# sideload -> better performance for larger datasets.


###################################
# Static content for all pages
###################################

# dark mode toggle
color_mode_switch = html.Button(
    className='fa fa-sun fa-moon',
    id='color-mode-switch',
    n_clicks=0,
    style={
        'border': 'none',
        'background': 'transparent',
        'cursor': 'pointer',
        'color': 'white'
    }
)

# navbar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(dbc.NavbarBrand('für fortnite!', class_name='ms-2'), width='auto'),
            dbc.Col(color_mode_switch),
        ], align='center', class_name='g-0'),
        
        dbc.Nav([
            dbc.NavItem(dbc.NavLink('home.', href='/')),
            dbc.NavItem(dbc.NavLink('about.', href='/about')),
        ], class_name='ms_auto'),
    ],  fluid=True),
        color='info',
        class_name='mb-2',
        id='content')

###################################

# Main layout that loads all static content and other pages.
app.layout = html.Div([
                    dcc.Location(id='url', refresh=False),
                    navbar,
                    dash.page_container
                    ])

###################################
# callbacks go here
# Darkmode toggle client callback.
clientside_callback(
    """
    (n_clicks) => {
    let isLightMode = n_clicks % 2 === 1;
    document.documentElement.setAttribute('data-bs-theme', isLightMode ? 'light' : 'dark');
    return isLightMode ? 'fa fa-sun' : 'fa fa-moon';
    }
    """,
    Output('color-mode-switch', 'className'),
    Input('color-mode-switch', 'n_clicks'),
)

# TODO In theory we should do handling of what happens when wrong
# paths are called but I honestly don't see myself doing that. Would
# be doable in a simple app.callback if anyone wants to do that.
###################################

if __name__ == "__main__":
    app.run(debug=True)