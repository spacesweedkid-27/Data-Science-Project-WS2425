'''
DS Project Website
Für Fortnite
'''
# TODO update requirements.txt
import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback, Patch
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.io as pio

app = Dash(__name__,
    external_stylesheets=[dbc.themes.MORPH, dbc.icons.FONT_AWESOME],
    use_pages=True
)
server=app.server

# We'll need to call some functions lateron to dynamically
# change the graphs generated on the embedded pages.
import pages.chords as c


###################################
# data imports go here
###################################
# Should probably load data within pages, so data gets rendered on view, not on
# sideload -> better performance for larger datasets.

###################################
# Design-specific stuff, do not touch or I'll cry.
###################################

templates = ['morph']
load_figure_template(templates)

###################################
# Static content for all pages
###################################

# Please try to keep this as clean as possible. This file's gonna be overloaded
# with callbacks and I don't wanna go searching for any data in here later on.

# Dark mode toggle component.
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

# Navbar component.
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(dbc.NavbarBrand('für fortnite!', class_name='ms-2'), width='auto'),
            dbc.Col(color_mode_switch), #  Dark mode toggle.
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
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    navbar,
    #  Holds dynamic page data.
    dash.page_container,
    #  Invisible storage for active theme.
    dcc.Store(id='theme-store', data = 'plotly_dark'),
], fluid=True)

###################################
# CALLBACKS
###################################

# GENERAL CALLBACKS
# you're a bold one

# Darkmode toggle client callback.
clientside_callback(
    # Why did I write this in JS? I don't know. But it
    # works now and I don't want to touch it ever again.
    """
    (n_clicks) => {
    let isLightMode = n_clicks % 2 === 1;
    document.documentElement.setAttribute('data-bs-theme',
                                            isLightMode ? 'light' : 'dark');
    return isLightMode ? 'fa fa-sun' : 'fa fa-moon';
    }
    """,
    Output('color-mode-switch', 'className'),
    Input('color-mode-switch', 'n_clicks'),
)
# Update theme-store when n_clicks in color-mode-switch changes.
@callback(
        Output('theme-store', 'data'),
        Input('color-mode-switch', 'n_clicks')
)
def update_theme_store(n_clicks):
    isLightMode = n_clicks % 2 == 1
    return 'morph' if isLightMode else 'plotly_dark'

# SPECIFIC CALLBACKS

# Sadly this must be done for any graphic, because it uses ids and ids are
# always object-bound and can't really be reused. I'll probably put the content
# of update_fig_template in an unbound function, so only Output and Input have
# to be defined and then function can be called. 

# Input for theme change is always color-mode-switch and n_clicks.
# Output is the specific figure's id and figure tag itself.

# Callback for theme switch for chord-frequency heatmap.
@callback(
    Output('heatmap', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_fig_template(n_clicks):
    isLightMode = n_clicks % 2 == 1
    template = pio.templates['morph'] if isLightMode else pio.templates['plotly_dark']
    
    patched_fig = Patch()
    patched_fig['layout']['template'] = template
    return patched_fig


# Callback for heatmap chord-frequency slider.
@callback(
    Output('heatmap', 'figure', allow_duplicate=True),
    [Input('frequency-threshold', 'value'),
     Input('theme-store', 'data')],
    prevent_initial_call=True
)
def update_heatmap(min_frequency, theme):
    filtered_matrix = c.chord_matrix.loc[:, c.chord_matrix.max(axis=0) >= min_frequency]
    updated_heatmap_fig = c.create_heatmap(filtered_matrix, theme)

    return updated_heatmap_fig

###################################

if __name__ == "__main__":
    app.run(debug=True)