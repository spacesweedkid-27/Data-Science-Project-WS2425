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

#  simple chords

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

init_heatmap = create_heatmap(chord_matrix, theme)

###################################
# CHORD PROGRESSIONS
###################################

## Pie-chart of main harmony and interval differences.
hs_h, hs_i = get_all_main_harmonies_and_intervals('data/merged.csv', {tuple() : 0}, {tuple() : 0})
df_h = pd.DataFrame(hs_h.items(), columns=['Harmonic Progression', 'Absolute Frequency'])
df_h = df_h.sort_values(by=['Absolute Frequency'], ascending=False)

#df_h.loc[df_h['Absolute Frequency'] < 10, 'Harmonic Progression'] = 'Progressions with Frequency less than 10'
df_h = df_h[(df_h['Absolute Frequency'] < 618) & (df_h['Absolute Frequency'] > 10)]
#pie_h = px.pie(df_h, values='Absolute Frequency', names='Harmonic Progression', title='Identified Harmonic Progression by Frequency')
bar_h = px.bar(df_h, x='Harmonic Progression', y='Absolute Frequency')
#bar_h = go.Figure(data=[go.Bar(x=df_h['Harmonic Progression'], y=df_h['Absolute Frequency'])])

# shows correct graph
#bar_h.show()

###################################
# CHORD GENRE RELATIONS
###################################

# Some content

###################################
# HTML ELEMENTS
###################################

# Slider to set a minimum threshold to the chords that are
# being displayed in the chord frequencies by year heatmap.
filter_slider = dcc.Slider(
    id = 'frequency-threshold',
    min = 0,
    max = chord_matrix.max().max(),
    step = 50,
    value = 1,
    marks = {
        i: str(i) for i in range(0, int(chord_matrix.max().max()) + 1, 200)
    }, tooltip = {'placement': 'bottom', 'always_visible': False},
    className = 'w-50'
)

fig = dbc.Container([
    html.H3('Chord Frequencies by Year'),
    filter_slider,
    dcc.Graph(
        id = 'heatmap',
        figure = init_heatmap,
    )
])

# somehow shows incorrect graph
fig_bar_h = dbc.Container([
    html.H3('Harmonic Progression by Absolute Frequency'),
    dcc.Graph(
        id = 'harmony-bar',
        figure = bar_h
    )
])

###################################


###################################
# MAIN LAYOUT
###################################


layout = html.Div([heading,
                   main_content,
                   fig,
                   fig_bar_h
                   ]
                )
