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
import nltk
from nltk.util import ngrams
import plotly.graph_objects as go
import plotly.express as px
from textblob import TextBlob
import numpy as np
from collections import Counter
from nltk.util import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import glob
import os
import re

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
    isDarkMode = n_clicks % 2 == 1
    template = pio.templates['plotly_dark'] if isDarkMode else pio.templates['morph']
    
    patched_fig = Patch()
    patched_fig['layout']['template'] = template

    if isDarkMode:
        patched_fig['layout']['paper_bgcolor'] = '#212529'
        patched_fig['layout']['plot_bgcolor'] = '#212529'
    
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
    dcc.Store(id='theme-store', data = 'morph'),
], fluid=True, class_name='mb-5')

#dcc.Store(id='lyrics-store', data='')  # Store for lyrics data

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
    let isDarkMode = n_clicks % 2 === 1;
    document.documentElement.setAttribute('data-bs-theme',
                                            isDarkMode ? 'dark' : 'light');
    return isDarkMode ? 'fa fa-sun' : 'fa fa-moon';
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
    isDarkMode = n_clicks % 2 == 1
    return 'plotly_dark' if isDarkMode else 'morph'

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

    filtered_matrix = chord_matrix.loc[:, pd.to_numeric(chord_matrix.max(axis=0)) >= int(min_frequency)]
    updated_heatmap_fig = c.create_heatmap(filtered_matrix, theme)

    if theme == 'plotly_dark':
        updated_heatmap_fig['layout']['paper_bgcolor'] = '#212529'
        updated_heatmap_fig['layout']['plot_bgcolor'] = '#212529'
    return updated_heatmap_fig

# Callback for chordfrequency by toptags slider.
@callback(
        Output('chords-toptags-bubble', 'figure'),
        Input('color-mode-switch', 'n_clicks')
)
def update_chords_toptags_bubble_theme(n_clicks):
    return update_fig_template(n_clicks)

@callback(
        Output('chords-toptags-bubble', 'figure', allow_duplicate = True),
        [Input('chords-toptags-bubble-slider', 'value'),
         Input('theme-store', 'data')],
         prevent_initial_call = True
)
def update_chords_toptags_bubble(min_frequency, theme):
    filtered_df = c.chords_toptags_counts_df[c.chords_toptags_counts_df['Count'] >= int(min_frequency)]
    updated = c.create_chords_toptags_bubble(filtered_df, theme)

    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'

    return updated

# Callbacks for harmony barchart. 
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
    updated = c.create_bar_chart_harmonic_progression(theme)

    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'
    return updated

@callback(
    Output('click-harmony', 'children'),
    Input('harmony-bar', 'clickData')
)
def on_click_harmony_bar(click):
    if not click:
        raise dash.exceptions.PreventUpdate

    # Harmony that has been clicked
    query = click['points'][0]['x']
    
    return html.P(f'Link to example of clicked harmony: {c.query_h(query)}')

# Callbacks for interval barchart
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
    updated = c.create_bar_chart_interval_progression(theme)
    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'
    return updated

# Callback for Interval Variance boxplot
@callback(
    Output('interval-var', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_interval_var(n_clicks):
    return update_fig_template(n_clicks)

# Callbacks for harmony top tags bubble
@callback(
    Output('harmonies-toptags-bubble', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_harmonies_toptags_bubble_theme(n_clicks):
    return update_fig_template(n_clicks)

@callback(
    Output('harmonies-toptags-bubble', 'figure', allow_duplicate=True),
    [Input('harmonies-toptags-bubble-slider', 'value'),
     Input('theme-store', 'data')],
    prevent_initial_call = True
)
def update_harmonies_toptags_bubble(min_frequency, theme):
    filtered_df = c.harmonies_toptags_count_df[c.harmonies_toptags_count_df['Count'] >= int(min_frequency)]
    updated = c.create_harmonies_toptags_bubble(filtered_df, theme)
    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'
    return updated


###################################
# TIME
###################################

@callback(
    Output('duration-years-bar', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_duration_years_bar_theme(n_clicks):
    return update_fig_template(n_clicks)

# Duration slider callback
@callback(
    Output('duration-years-bar', 'figure', allow_duplicate=True),
   [Input('duration-years-bar-toggle', 'value'),
    Input('theme-store', 'data')],
    prevent_initial_call = True
)
def update_duration_years_bar(show_outliers, theme):
    updated = t.create_duration_years_bar_with_outliers(show_outliers, theme)
    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'
    return updated

# Duration Boxplot Themeswitch.
@callback(
    Output('duration-boxplot', 'figure'),
    Input('theme-store', 'data')
)
def update_duration_boxplot(theme):
    updated = t.create_duration_boxplot(theme)
    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'
    return updated

# Tempo Scatter Plot Themeswitch.
@callback(
    Output('tempo-plot', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_tempo_plot_theme(n_clicks):
    return update_fig_template(n_clicks)

# Tempo range slider
@callback(
    Output('tempo-plot', 'figure', allow_duplicate=True),
   [Input('tempo-year-range-slider', 'value'),
    Input('theme-store', 'data')],
    prevent_initial_call = True
)
def update_tempo_plot(year_range, theme):
    updated = t.create_tempo_plot_with_range(year_range, theme)
    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = '#212529'
        updated['layout']['plot_bgcolor'] = '#212529'
    return updated

###################################
# LYRICS
###################################

@callback(
    Output('wordcloud', 'figure'),
    Input('color-mode-switch', 'n_clicks')
)
def update_wordcloud(n_clicks):
    isDarkMode = n_clicks % 2 == 1
    if isDarkMode:

        bg_color = '#212529'
    else:
        bg_color = '#d9e3f1'
    
    return l.create_wordcloud(bg_color, l.all_lyrics)

# TODO slider wordcloud when rerendering

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
    prevent_initial_call = True
)
def update_xaxis_yaxis_figtype(value):
    <update logic>
    updated = t.create_xaxis_yaxis_figtype(theme)

    if theme == 'plotly_dark':
        updated['layout']['paper_bgcolor'] = #212529
        updated['layout']['plot_bgcolor'] = #212529
    return updated
'''

###################################

if __name__ == "__main__":
    app.run(debug=True)