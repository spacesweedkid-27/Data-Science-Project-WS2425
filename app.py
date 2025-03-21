'''
DS Project Website
Für Fortnite
'''

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
import pages.lyrics as l
import pages.tempo as t

import data_collection.scripts.numerize_chords as nc


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

def update_fig_template(n_clicks):
    isLightMode = n_clicks % 2 == 1
    template = pio.templates['morph'] if isLightMode else pio.templates['plotly_dark']
    
    patched_fig = Patch()
    patched_fig['layout']['template'] = template
    return patched_fig

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
    Output('chordfrequency-year-heatmap', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_chordfrequency_year_heatmap(n_clicks):
    return update_fig_template(n_clicks)

# Callback for heatmap chord-frequency slider and shrink toggle.
@callback(
    Output('chordfrequency-year-heatmap', 'figure', allow_duplicate=True),
    [Input('chordfrequency-year-slider', 'value'),
     Input('chordfrequency-year-shrinkchord-toggle', 'value'), # new
     Input('theme-store', 'data')],
    prevent_initial_call=True
)
def update_heatmap(min_frequency, shrink_chords, theme):
    chord_matrix = c.chord_matrix.copy()

    # If shrink chords toggle is true, parse "special" chords into "normal" ones
    if shrink_chords:
        chord_matrix.columns = chord_matrix.columns.map(nc.shrink_chord)
        chord_matrix = chord_matrix.T.groupby(level=0).sum().T

    filtered_matrix = chord_matrix.loc[:, chord_matrix.max(axis=0) >= min_frequency]
    updated_heatmap_fig = c.create_heatmap(filtered_matrix, theme)

    return updated_heatmap_fig

@callback(
    Output('harmony-bar', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_harmony_bar(n_clicks):
    return update_fig_template(n_clicks)

@callback(
    Output('harmony-bar', 'figure', allow_duplicate=True),
   [Input('frequency-threshold-harmony-bar', 'value'),
    Input('theme-store', 'data')],
    prevent_initial_call=True
)
def update_bar_chart_harmony(min_frequency, theme):
    c.df_h = c.df_h_orig.loc[c.df_h_orig['Absolute Frequency'] >= min_frequency]
    return c.create_bar_chart_harmonic_progression(theme)

@callback(
    Output('interval-bar', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_interval_bar(n_clicks):
    return update_fig_template(n_clicks)

@callback(
    Output('interval-bar', 'figure', allow_duplicate=True),
   [Input('frequency-threshold-interval-bar', 'value'),
    Input('theme-store', 'data')],
    prevent_initial_call=True
)
def update_bar_chart_interval(min_frequency, theme):
    c.df_i = c.df_i_orig.loc[c.df_i_orig['Absolute Frequency'] >= min_frequency]
    return c.create_bar_chart_interval_progression(theme)


###################################
# GRAPH TEMPLATE pt.3
###################################

# Callbacks are necessary for the handling of sliders and the theme-toggle.
# If you don't use any interactive elements such as sliders, you still need
# to create one callback to apply the theme to the function. This is fairly
# straightforward, though.
'''
# Theme switch callback for xaxis yaxis figtype.
@callback(
    Output('xaxis-yaxis-figtype', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_xaxis_yaxis_figtype(n_clicks):
    return update_fig_template(n_clicks)
'''

# When using a slider or other filter options, you'll need a callback that
# handles value changes as well as theme changes (because the figure will be
# re-rendered and is assigned the default theme on load. We access the invisible
# theme-store html element to fetch the currently selected theme to apply it on
# re-render automatically.)
# You'll need to call the create function you defined in the corresponding
# subpage. All subpages are imported already. Use:
# c.function for functions from the chord-page
# t.function for functions from the tempo-page
# l.function for functions from the lyrics-page
'''
# Callback for xaxis yaxis figtype slider (toggle, switch, ...)
@callback(
    Output('xaxis-yaxis-figtype', 'figure', allow_duplicate=True),
   [Input('xaxis-yaxis-fitype-slider', 'value'),
    Input('theme-store', 'data')],
    precent_initial_call = True
)
def update_xaxis_yaxis_figtype(value):
    <update logic>
    return t.create_xaxis_yaxis_figtype(theme)
'''

###################################

if __name__ == "__main__":
    app.run(debug=True)