# General imports
import ast
import glob
import os
import csv

# Dash related imports
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_bootstrap_templates import load_figure_template

# Plot related imports
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_collection.scripts.progression_by_frequency import get_all_main_harmonies_and_intervals

import data_collection.scripts.numerize_chords as nc

dash.register_page(__name__)

load_figure_template('morph')
theme = 'morph' #  Initial theme that needs to be passed to graphs on load

heading = dbc.Container('We got some information about chords here')
main_content = dbc.Container('Some information about this project goes here. '
'This content answers questions about what data sources we used, how the data '
'was processed and what assumptions were made. Whilest this information not '
'being listed in the official requirements provided by CAU, it still holds a lot'
'of value from a scientific standpoint.')

path = 'data/chords_extracted'
files = glob.glob(os.path.join(path, 'billboard_*.csv'))
TAGS_PATH = 'data/Billboard_lyrics/Billboard_Lyrics_Top_Tags'

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
        try: #  Gracefully (tm) handle 'not found' instances
            chord_list = ast.literal_eval(chords) #  String to List
            chord_list = list(set(chord_list))
            counts.extend(chord_list)
        except (KeyError, ValueError):
            continue
    
    count_per_year[year] = counts

# The following df modifications were assisted by chatGPT (up until the
# create_heatmap() function definition).

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
        template = theme,
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
    bar_h.update_layout(
        template=theme)
    return bar_h
def create_bar_chart_interval_progression(theme: str) -> go.Figure:
    bar_i = px.bar(df_i, x='Interval Progression', y='Absolute Frequency')
    bar_i.update_layout(
        template=theme)
    return bar_i

init_bar_h = create_bar_chart_harmonic_progression(theme)
init_bar_i = create_bar_chart_interval_progression(theme)

# Query a specific harmonic progression.
def query_h(query: str) -> str:
    """Returns a link to a harmonic progression."""
    with open('data/merged.csv', newline='', encoding='utf-8') as csvfile:
        # ...
        reader = csv.DictReader(csvfile)
        songs = list(reader)
        songs.sort(key=lambda x:-eval(x['Year']) + eval(x['Rank']))
        for song in songs:
            if song['Main_Harmony'] == query:
                return song['UG_link']
    raise Exception('Shit shit shit, missing data!')

def create_scatterplot_interval_variance(theme: str) -> go.Figure:
    with open('data/merged.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)
        for song in songs:
            song['Year'] = eval(song['Year'])
            #song['Rank'] = eval(song['Rank'])
            song['Interval_Variance'] = eval(song['Interval_Variance']) if song['Interval_Variance'] != 'not found' else 0.0
    as_df = pd.DataFrame.from_records(songs)
    scat = px.box(as_df, x='Year', y='Interval_Variance')
    median = as_df.groupby('Year', as_index=False)['Interval_Variance'].median()
    scat.add_trace(go.Scatter(x=median['Year'], y=median['Interval_Variance'], mode='lines', name='Median', line=dict(color="red")))
    scat.update_layout(
        template=theme)
    return scat

init_scat = create_scatterplot_interval_variance(theme)

###################################
# CHORD GENRE RELATIONS
###################################

def apply_literal_eval(val):
    '''Helper to catch errors for not found instances in chord data.'''
    if isinstance(val, str):
        try:
            return ast.literal_eval(val)
        except (ValueError):
            return []
def toptags_to_list(val):
    '''Helper to turn comma-separated Top_Tag strings into lists.'''
    if isinstance(val, str):
        return [tag.strip() for tag in val.split(',')]
    return []

chords_df = pd.read_csv('data/merged.csv', usecols=['Year', 'Title',
                                                 'Artist', 'Chords'])
# Turn chords into list objects.
chords_df['Chords'] = chords_df['Chords'].apply(apply_literal_eval)

# The following df modifications were assisted by chatGPT (up until the 
# create_chords_toptags_bubble() function definition).

# Merge all tags files into one dataframe.
tags_file_path = glob.glob(
    'data/Billboard_lyrics/BillBoard_Lyrics_Top_Tags' + '/*.csv')
tags_list = (pd.read_csv(file, usecols=['Title', 'Artist', 'Top_Tags'])
    for file in tags_file_path)
toptags_df = pd.concat(tags_list, ignore_index=True)
# Turn Top_Tags strings into list objects
toptags_df['Top_Tags'] = toptags_df['Top_Tags'].apply(toptags_to_list)

# Merged dataframe
chords_toptags_df = pd.merge(
    chords_df, toptags_df, on = ['Title', 'Artist'], how='inner')

chords_toptags_exploded_df = chords_toptags_df.explode(
    'Chords').explode('Top_Tags')

# Shrink chords (because on very convoluted axis is enough)
chords_toptags_exploded_df['Chords'] = chords_toptags_exploded_df['Chords'].fillna(
    '').apply(nc.shrink_chord)

# Drop duplicates to only count one occurence of each chord per song.
chords_toptags_exploded_df = chords_toptags_exploded_df.drop_duplicates(
    subset=['Title', 'Artist', 'Chords', 'Top_Tags'])

chords_toptags_counts_df = chords_toptags_exploded_df.groupby(
    ['Chords', 'Top_Tags']).size().reset_index(name='Count')

def create_chords_toptags_bubble(df, theme: str):
    chords_toptags_bubble = go.Figure(data = px.scatter(
        df,
        x = 'Top_Tags',
        y = 'Chords',
        size='Count',
    ))
    
    chords_toptags_bubble.update_layout(
        # axis titles and so on
        autosize = True,
        height = 600, #  Can be changed to different value when it makes sense
        template = theme
    )
    return chords_toptags_bubble

init_chords_toptags_bubble = create_chords_toptags_bubble(chords_toptags_counts_df, theme)

###################################
# PROGRESSION GENRE RELATIONS
###################################

harmonies_df = pd.read_csv('data/merged.csv', usecols=['Year', 'Title',
                                                 'Artist', 'Main_Harmony'])

harmonies_toptags_df = pd.merge(harmonies_df, toptags_df, on = ['Title', 'Artist'],
                              how = 'inner')
harmonies_toptags_exploded_df = harmonies_toptags_df.explode(
    'Main_Harmony').explode('Top_Tags')
# Remove any not found instances from the dataframe.
harmonies_toptags_exploded_df = harmonies_toptags_exploded_df[
    (harmonies_toptags_exploded_df['Main_Harmony'] != 'not found') &
    (harmonies_toptags_exploded_df['Top_Tags'] != 'not found')]
harmonies_toptags_count_df = harmonies_toptags_exploded_df.groupby(
    ['Main_Harmony', 'Top_Tags']).size().reset_index(name = 'Count')

def create_harmonies_toptags_bubble(df, theme: str):
    htb = go.Figure(data = px.scatter(
        df,
        y = 'Top_Tags',
        x = 'Main_Harmony',
        size = 'Count'
    ))
    htb.update_layout(
        autosize = True,
        height = 600,
        template = theme,
    )
    return htb

init_harmonies_toptags_bubble = create_harmonies_toptags_bubble(
    harmonies_toptags_count_df, theme)

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
    step = 1,
    value = 1,
    marks = {
        i: str(i) for i in range(0, int(chord_matrix.max().max()) + 1, 10)
    }, tooltip = {'placement': 'bottom', 'always_visible': False}
) 
# Toggles for shrinking the chords and re-rendering graph accordingly.
chordfrequency_year_shrinkchord_toggle = dbc.Switch(
    id = 'chordfrequency-year-shrinkchord-toggle',
    label = 'shrink chords',
    value = False
)

chordfrequency_year_text = dbc.Container(
    '''Musicians often write songs in the same key that they can sing in and 
    therefore use the same chords more often. Most of the most frequently used 
    chords can be played within the C-major or A-minor scale. We can also see, 
    that the A-minor key is more popular than the C-major key, since D and Em 
    work better in A-minor compared to C-major, with D and Em being roughly the 
    IV and V of A-minor, but the II and II of C-major which are less important 
    harmonix chords. ''',
    class_name = 'mb-3'
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
    chordfrequency_year_text,
    chordfrequency_year_controls,
    dcc.Graph(
        id = 'chordfrequency-year-heatmap',
        figure = init_chordfrequency_year_heatmap,
    )
], class_name='mb-5')

###################################
# CHORDFREQUENCY BY TOP TAGS

chords_toptags_bubble_slider = dcc.Slider(
    # Slider
    id = 'chords-toptags-bubble-slider',
    min = 0,
    max = chords_toptags_counts_df['Count'].max(),
    step = 5,
    value = 1,
    marks = {
        i: str(i) for i in range(0, int(chords_toptags_counts_df['Count'].max()) + 5, 50)
    }, tooltip = {'placement': 'bottom', 'always_visible': False}
)

chords_toptags_text = dbc.Container(
    '''It shouldn\'t be surprising, that the most frequent genre in popular 
    music is pop-music. Looking at the top user generated tags from LastFM and
    comparing them to the chord frequency, we can see that Hip-Hop and Rap are 
    also quite popular. We can also identify that these two genres have the most 
    missing chords which can be explained by their neglection of harmony, since 
    they focus more on rhythm and rhyme. ''',
    class_name = 'mb-3'
)

chords_toptags_info_text = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col(class_name='fa-regular fa-lightbulb', width = 'auto'),
            dbc.Col(html.H5('info', className = 'card-title align-top'))
        ]),
        html.P(
            '''
            Please be aware, that all top-tags we derived from the 
            last.FM API are user-generated. We distance ourself from any 
            political, cultural and social statements that might have 
            influenced the most frequent tags.
            ''', className = 'mb-0'
        )], class_name='p-2 p2-5 ps-5'
    )
    ], color = 'secondary', class_name='mb-4 p-2'
)

chords_toptags_bubble_controls = dbc.Row([
    dbc.Col(chords_toptags_bubble_slider),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
            id = 'chords-toptags-slider-info',
            style = {'cursor': 'pointer'},
            width = 'auto'),
    dbc.Col(
        dbc.Tooltip(
            'Sets a threshold for the minimum tag frequency to be displayed. '
            'Tags with a lower frequency than the threshold are not displayed '
            'in the graph.',
            target = 'chords-toptags-slider-info',
            placement = 'right'
        )
    )
])

chords_toptags_bubble_fig = dbc.Container([
    html.H3('Absolute Chordfrequency by Top Tags'),
    chords_toptags_text,
    chords_toptags_info_text,
    chords_toptags_bubble_controls,
    dcc.Graph(
        id = 'chords-toptags-bubble',
        figure = init_chords_toptags_bubble
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

harmony_frequency_text = dbc.Container(
    '''What main chord repition should you use to write the perfect song? By 
    scraping chords, identifying their key signature to transpose equal 
    harmonies and looking for repeated patterns, we found the most frequently 
    used harmonic progressions of the last 20 years. \n
    The most used harmonic progression (I, VI, III, VII) can for example be 
    played in B-Minor with chords Bm, G, D, A, like in Ed Sheeran's "Shivers". ''',
    class_name = 'mb-3'
)

harmony_frequency_info_text = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col(class_name='fa-regular fa-lightbulb', width = 'auto'),
            dbc.Col(html.H5('info', className = 'card-title align-top'))
        ]),
        html.P(
            '''
            By clicking on one of the bars for a harmonic progression a link 
            to chords of a song using the progression will be displayed above 
            the plot.
            ''', className = 'mb-0'
        )], class_name='p-2 p2-5 ps-5'
    )
    ], color = 'secondary', class_name='mb-4 p-2'
)

harmony_clicked_container = dbc.Container(id='click-harmony')

fig_bar_h = dbc.Container([
    html.H3('Harmonic Progression by Absolute Frequency'),
    harmony_frequency_text,
    harmony_frequency_info_text,
    harmony_frequency_bar_controls,
    harmony_clicked_container,
    dcc.Graph(
        id = 'harmony-bar',
        figure = init_bar_h
    ),
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
    html.P("""
        Here we look at the intervals that are repeated most frequently in a song.
        It should be noted, that the intervals are in half-steps and calculated using
        the minimal distance either left or right to the next note.
        
        This is why the intervals don't add up to 0, even though they arrive at the
        same key. For example the most frequent would be (C, G, D, E) if the first note played is C.

        These notes are all in C-major which could mean that the progression (I, V, II, III)
        could have been played in major mode.

        So by looking at these half-steps we can determine the main harmony without knowing the key.
        """),
    interval_frequency_bar_controls,
    dcc.Graph(
        id = 'interval-bar',
        figure = init_bar_i
    )
], class_name='mb-5')

###################################
# MAIN HARMONIES BY TOPTAGS

harmonies_toptags_bubble_slider = dcc.Slider(
    # Slider
    id = 'harmonies-toptags-bubble-slider',
    min = 0,
    max = harmonies_toptags_count_df['Count'].max(),
    step = 1,
    value = 1,
    marks = {
        i: str(i) for i in range(0, int(harmonies_toptags_count_df['Count'].max()) + 1, 5)
    }, tooltip = {'placement': 'bottom', 'always_visible': False}
)

harmonies_toptags_bubble_controls = dbc.Row([
    dbc.Col(harmonies_toptags_bubble_slider),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
            id = 'harmonies-toptags-slider-info',
            style = {'cursor': 'pointer'},
            width = 'auto'),
    dbc.Col(
        dbc.Tooltip(
            'Sets a threshold for the minimum tag frequency to be displayed. '
            'Tags with a lower frequency than the threshold are not displayed '
            'in the graph.',
            target = 'harmonies-toptags-slider-info',
            placement = 'right'
        )
    )
])

harmonies_toptags_bubble_fig = dbc.Container([
    html.H3('Main Harmony absolute frequency by Top Tags'),
    """Here we look at which tags contain which main harmony shown in the last graph.
    It is very interesting to see, that the progressions (0,0,0,0) and (1,1,1,1) have
    high rap and hip-hop matches, that if we add them together even overcome the pop matches.""",
    harmonies_toptags_bubble_controls,
    dcc.Graph(
        id = 'harmonies-toptags-bubble',
        figure = init_harmonies_toptags_bubble
    )
], class_name = 'mb-5')

###################################
# INTERVAL VARIANCE

fig_var = dbc.Container([
    html.H3('Variance of Interval-Length over Year'),
        html.P("""
        The last graph searched for patterns in the half-steps,
        here we look at the amount of half-steps overall:
        
        We calculated for each song the variance of half-tone steps.
        This means we looked at each played interval in every song
        and calculated the variance of the length of them.
        
        With this we get a measure of how _interesting_ each song is.
        For example if we would just play between two notes over and over,
        we'd have little variance according to this measure,
        even though the absolute distance median would add up high.

        The following graph shows how this average variance changed over the years.
        """),
    dcc.Graph(
        id = 'interval-var',
        figure = init_scat
    )
], class_name='mb-5')

###################################


###################################

# META TEXT
meta = dbc.Container([
    html.H3('About the chords'),
        html.P(
            """
            We searched with an automatic search query injector for 2000 Songs, of these we received 1382 chords. The remaining 618 were missing due to either:

            1. Broken search results

            2. Only non-free chords available or no public chords found
             
            3. Labels/artists blocking chord pages due to copyright etc.

            Since the algorithm picked the first link that contains the song's title and artist, and the links were normally sorted by ratings, this meant that for the most popular songs we got correct results.  
            Some songs that didn't stand the test of time, which were coincidentally rap/hip-hop songs, did have chords that didn't make sense if you listen to the music. This wasn't that much of an issue though, since their \"harmony\" didn't matter that much.
            """
    )
])
###################################

###################################
# MAIN LAYOUT
###################################


layout = dbc.Container([#heading,
                   meta,
                   #main_content,
                   fig,
                   chords_toptags_bubble_fig,
                   fig_bar_h,
                   harmonies_toptags_bubble_fig,
                   fig_bar_i,
                   fig_var
                   ],
                   class_name='mw-75'
                )
