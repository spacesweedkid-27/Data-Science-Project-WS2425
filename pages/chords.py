import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import ast
import glob
import os
from dash_bootstrap_templates import load_figure_template
from data_collection.scripts.progression_by_frequency import get_all_main_harmonies_and_intervals

dash.register_page(__name__)

load_figure_template('morph')
theme = 'plotly_dark' #  Initial theme that needs to be passed to graphs on load

heading = dbc.Container('We got some information about chords here')
main_content = dbc.Container('Some information about this project goes here. '
'This content answers questions about what data sources we used, how the data '
'was processed and what assumptions were made. Whilest this information not '
'being listed in the official requirements provided by CAU, it still holds a lot'
'of value from a scientific standpoint.')

path = 'data/chords_extracted'
files = glob.glob(os.path.join(path, 'billboard_*.csv'))

###################################
# CHORD FREQUENCY BY YEAR
###################################

# This was written before we had the accumulated data file.
# Might rewrite this later if there's time.

# Store chord frequencies.
count_per_year = {}
for file in files: 
    year = file.split('_')[-1].split('.')[0] #  get part of filename between _ and .

    # Load data into dataframe
    df = pd.read_csv(file)

    # Holds count for every year
    counts = []

    # For each song, put 
    for chords in df['Chords']:
        try: #  Gracefully handle 'not found' instances
            chord_list = ast.literal_eval(chords) #  String to List
            counts.extend(chord_list)
        except (KeyError, ValueError):
            continue
    
    count_per_year[year] = counts

all_chords = list(set([chord for year_data in count_per_year.values()
                            for chord in year_data]))
sorted_years = sorted(count_per_year.keys())

chord_matrix = pd.DataFrame(columns=all_chords, index=sorted_years)

for year, chords in count_per_year.items():
    chord_counts = {chord: chords.count(chord) for chord in all_chords}
    chord_matrix.loc[year] = chord_counts

chord_matrix = chord_matrix.apply(pd.to_numeric, errors='coerce').fillna(0)
def create_heatmap(chord_matrix, theme):
    heatmap = go.Figure(data=go.Heatmap(
        z = chord_matrix.values,
        x = chord_matrix.columns,
        y = chord_matrix.index,
        colorscale = 'Blues',
        colorbar = dict(title='Chord Frequency'),
        )
    )
        
    heatmap.update_layout(
        xaxis_title='Chords',
        yaxis_title='Year',
        autosize=True,
        xaxis=dict(tickangle=45),
        yaxis=dict(tickmode='linear'),
        height = 600,
        template = theme
    )

    return heatmap

init_chordfrequency_year_heatmap = create_heatmap(chord_matrix, theme)

###################################
# CHORD PROGRESSIONS
###################################

## Pie-chart of main harmony and interval differences.
hs_h, hs_i = get_all_main_harmonies_and_intervals('data/merged.csv', {tuple() : 0}, {tuple() : 0})
df_h_orig = pd.DataFrame(hs_h.items(), columns=['Harmonic Progression', 'Absolute Frequency'])
df_i_orig = pd.DataFrame(hs_i.items(), columns=['Interval Progression', 'Absolute Frequency'])

# The first element is the 'not found' case.
df_h_orig = df_h_orig[1:]
df_h_orig = df_h_orig.sort_values(by=['Absolute Frequency'], ascending=False)
df_i_orig = df_i_orig[1:]
df_i_orig = df_i_orig.sort_values(by=['Absolute Frequency'], ascending=False)

# With no filter we just copy.
df_h = df_h_orig
df_i = df_i_orig

def create_bar_chart_harmonic_progression(theme: str) -> go.Figure:
    bar_h = px.bar(df_h, x='Harmonic Progression', y='Absolute Frequency')
    bar_h.update_layout(template=theme)
    return bar_h
def create_bar_chart_interval_progression(theme: str) -> go.Figure:
    bar_i = px.bar(df_i, x='Interval Progression', y='Absolute Frequency')
    bar_i.update_layout(template=theme)
    return bar_i

init_bar_h = create_bar_chart_harmonic_progression(theme)
init_bar_i = create_bar_chart_interval_progression(theme)

###################################
# CHORD GENRE RELATIONS
###################################

# Some content

###################################
# HTML ELEMENTS
###################################

###################################
# CHORD FREQUENCY BY YEAR

# Slider to set a minimum threshold to the chords that are
# being displayed in the chord frequencies by year heatmap.
chordfrequency_year_slider = dcc.Slider(
    id = 'chordfrequency-year-slider',
    min = 0,
    max = chord_matrix.max().max(),
    step = 50,
    value = 1,
    marks = {
        i: str(i) for i in range(0, int(chord_matrix.max().max()) + 1, 200)
    }, tooltip = {'placement': 'bottom', 'always_visible': False}
)
# Toggles for shrinking the chords and re-rendering graph accordingly.
chordfrequency_year_shrinkchord_toggle = dbc.Switch(
    id = 'chordfrequency-year-shrinkchord-toggle',
    label = 'shrink chords',
    value = False
)

# Wrapper for chordfrequency year controls.
chordfrequency_year_controls = dbc.Row([
    # Slider
    dbc.Col(chordfrequency_year_slider, width=5),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
                id = 'chordfrequency-year-slider-info',
                style = {'cursor': 'pointer'},
                width = 'auto'),
    dbc.Col(
        dbc.Tooltip(
            'Sets a threshold for the minimum chord frequency to be displayed. '
            'Chords with a lower frequency than the threshold are not displayed '
            'in the graph.',
            target = 'chordfrequency-year-slider-info',
            placement = 'right'
        )
    ),
    # Toggle
    dbc.Col(chordfrequency_year_shrinkchord_toggle),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
                id = 'chordfrequency-year-toggle-info',
                style = {'cursor': 'pointer'},
                width = 'auto'),
    dbc.Col(
        dbc.Tooltip(
            'Activates chord shrinking. With this setting activated, \'special\' '
            'chords such as Amaj7, are turned into their \'normal\' variants '
            'and the graph is re-rendered to account for these changes.',
                target = 'chordfrequency-year-toggle-info',
                placement = 'right'
        )
    )
])

fig = dbc.Container([
    html.H3('Chord Frequency by Year'),
    chordfrequency_year_controls,
    dcc.Graph(
        id = 'chordfrequency-year-heatmap',
        figure = init_chordfrequency_year_heatmap,
    )
], class_name='mb-5')

###################################
# HARMONIC PROGRESSION BY FREQUENCY

filter_slider_harmony = dcc.Slider(
    id = 'frequency-threshold-harmony-bar',
    min = 1,
    max = 52,
    step = 1,
    value = 1,
    marks = {
        i: str(i) for i in range(0, 52, 10)
    }, tooltip = {'placement': 'bottom', 'always_visible': False}
)

harmony_frequency_bar_controls = dbc.Row([
    # Slider
    dbc.Col(filter_slider_harmony),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
            id = 'harmony-frequency-slider-info',
            style = {'cursor': 'pointer'},
            width = 'auto'),
    dbc.Col(
        dbc.Tooltip(
            'Sets a threshold for the minimum frequency to be displayed. '
            'Progressions with a lower frequency than the threshold are not '
            'displayed in the graph.',
            target = 'harmony-frequency-slider-info',
            placement = 'right'
        )
    )
])

fig_bar_h = dbc.Container([
    html.H3('Harmonic Progression by Absolute Frequency'),
    harmony_frequency_bar_controls,
    dcc.Graph(
        id = 'harmony-bar',
        figure = init_bar_h
    )
], class_name='mb-5')

###################################

# INTERVAL PROGRESSION BY FREQUENCY

filter_slider_interval = dcc.Slider(
    id = 'frequency-threshold-interval-bar',
    min = 1,
    max = 52,
    step = 1,
    value = 1,
    marks = {
        i: str(i) for i in range(0, 52, 10)
    }, tooltip = {'placement': 'bottom', 'always_visible': False}
)

interval_frequency_bar_controls = dbc.Row([
    # Slider
    dbc.Col(filter_slider_interval),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
            id = 'interval-frequency-slider-info',
            style = {'cursor': 'pointer'},
            width = 'auto'),
    dbc.Col(
        dbc.Tooltip(
            'Sets a threshold for the minimum frequency to be displayed. '
            'Progressions with a lower frequency than the threshold are not '
            'displayed in the graph.',
            target = 'interval-frequency-slider-info',
            placement = 'right'
        )
    )
])

fig_bar_i = dbc.Container([
    html.H3('Interval Progression by Absolute Frequency'),
    interval_frequency_bar_controls,
    dcc.Graph(
        id = 'interval-bar',
        figure = init_bar_i
    )
], class_name='mb-5')

###################################


###################################
# MAIN LAYOUT
###################################


layout = dbc.Container([heading,
                   main_content,
                   fig,
                   fig_bar_h,
                   fig_bar_i
                   ],
                   class_name='mw-75'
                )
