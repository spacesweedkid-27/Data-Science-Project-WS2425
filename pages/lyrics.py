import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
from collections import Counter
from wordcloud import WordCloud
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import glob
import os
import re
import random
import matplotlib as mpl
import numpy as np # Sorry
import ast
from matplotlib.colors import ListedColormap

dash.register_page(__name__)

load_figure_template('morph')
theme = 'morph' #  Initial theme that needs to be passed to graphs on load
bg_color = '#d9e3f1'

heading = dbc.Container(html.H3('About the lyrics'))
main_content = dbc.Container(
    '''For many people the words of a song is what they relate to most. In this 
    section we take a deeper look into the verbal contents of songs. Using the 
    Genius API we created a dataset containing lyrics for most songs from 
    the Billboard End of Year Top 100 from 2005 to 2024. The following plots 
    display the results of analyzing them using different tools such as nltk and
    WordBlob. Further studies might look for correlations between polarity of 
    lyrics and genres. While we originally planned to do exactly that, the lack 
    of accurate genre data proved this endaevor too complicated for the scope of 
    this project.''')

# Verzeichnis und CSV-Dateien laden
folder_path = "data/Billboard_lyrics/Billboard_Lyrics_preprocessed/"
file_paths = glob.glob(os.path.join(folder_path, "billboard_*.csv"))

###################################
# GRAPHS
###################################

# Import or define your graphs here.
# Create one section (### #TITLE ###) for each graph. This makes it easier
# to look for certain elements. Try to keep naming precise.


# Prepare Data for Analysis
# Load and combine all data
dataframes = []
for file in file_paths:
    filename = os.path.basename(file)
    match = re.search(r'(\d{4})', filename)
    if match:
        year = int(match.group(1))
    else:
        continue
    df = pd.read_csv(file)
    df['Year'] = year  
    dataframes.append(df)

all_data = pd.concat(dataframes, ignore_index=True)

# Create all_lyrics here
all_lyrics = " ".join(all_data["Lyrics"].dropna()).lower()

# Define STOP_WORDS
STOP_WORDS = {"wan", "na", "ta", "ca", 'nigga'}

###################################
# POLARITY CHART INTERACTIVE

polarity_data = pd.read_csv('data/Billboard_lyrics/polarity/polarity.csv', usecols=['Year','Polarity'])
polarity_df = pd.DataFrame(data = polarity_data)
years = list(range(2005, 2025))

def create_polarity_year_chart(theme):    
    polarities_by_year = {year: [] for year in years}
    mean_polarities = {}

    for year in years:
        yearly_data = polarity_df[polarity_df['Year'] == year]
        if not yearly_data.empty:
            all_polarities = [p for sublist in yearly_data['Polarity'].apply(ast.literal_eval) for p in sublist]
            polarities_by_year[year] = all_polarities
            mean_polarities[year] = np.mean(all_polarities) if all_polarities else 0  # Durchschnitt berechnen
        else:
            mean_polarities[year] = 0
    
    fig = go.Figure()

    for year in years:
        polarities = np.array(polarities_by_year[year])
        
        # Trennen der neutralen Werte (Polarität = 0)
        negative = polarities[polarities < 0]
        neutral = polarities[polarities == 0]
        positive = polarities[polarities > 0]

        # Histogramme für jede Polaritätsklasse
        fig.add_trace(go.Histogram(
            x=negative,
            name=f'Negative ({year})',
            marker_color='red',
            opacity=0.7,
            visible=True if year in years else False
        ))

        fig.add_trace(go.Histogram(
            x=positive,
            name=f'Positive ({year})',
            marker_color='blue',
            opacity=0.7,
            visible=True if year in years else False
        ))

        fig.add_trace(go.Histogram(
            x=neutral,
            name=f'Neutral ({year})',
            marker_color='gray',
            opacity=0.5,
            visible=True if year in years else False
        ))

        # Durchschnittliche Polarität als dünne vertikale Linie 
        fig.add_trace(go.Scatter(
            x=[mean_polarities[year], mean_polarities[year]],  # Linie bei Durchschnittswert
            y=[1, 10**5],  # Höhe der Linie (angepasst für logarithmische Skalierung)
            mode="lines",
            line=dict(color="orange", width=2, dash="dash"),  # Farbe: Orange, Dünn, Gestrichelt
            name=f'Mean ({year})',
            visible=True if year in years else False
        ))

    steps = []
    for i, year in enumerate(years):
        step = dict(
            method="update",
            args=[{"visible": [j // 4 == i for j in range(len(years) * 4)]}],
            label=str(year)
        )
        steps.append(step)

    fig.update_layout(
        xaxis_title="Polarity",
        yaxis_title="Number of words",
        barmode='overlay',  # Histogramme überlagern sich leicht für bessere Sichtbarkeit
        yaxis_type="log",  # Logarithmische Skalierung
        sliders=[{
            "active": 0,  # Startjahr 2005
            "currentvalue": {
                "visible": True,
                "prefix": "Jahr: ",
                "font": {"size": 20}
            },
            "steps": steps
        }]
    )
    fig.update_layout(
        autosize = True,
        height = 600,
        template = theme
    )
    return fig

init_polarity_years_chart = create_polarity_year_chart(theme)

###################################
# POLARITY AVERAGE OVER YEAR

def create_polarity_mean_years_bar(theme):
    #fig = make_subplots(rows = 1, cols = 1, subplot_titles = [''])

    mean_pol = []
    years = []

    for year in range(2005, 2025):
        year_data = polarity_df[polarity_df['Year'] == year]
        #print(year_data.head())

        if not year_data.empty:
            year_data.loc[:,'Polarity'] = year_data.loc[:,'Polarity'].apply(ast.literal_eval)
            year_data_exploded = year_data.explode('Polarity')
            avg_polarity = year_data_exploded.mean()
            
            # This is probably not necessary, but I get confused when dealing
            # with exploded dataframes, so I'll just append the values I want
            # to a list to create the dataframe from those lists. Not pretty,
            # but it works.
            years.append(year)
            mean_pol.append(avg_polarity['Polarity'])


    df = pd.DataFrame({
        'Year': years,
        'Polarity': mean_pol
    })
    fig = px.bar(df, x = 'Year', y = 'Polarity')

    fig.update_layout(
        autosize = True,
        
        xaxis_title = "Year",
        yaxis_title="Mean Polarity",
        showlegend=False,  
        hovermode="closest",
        template = theme,
        xaxis=dict(
            type="category",  # Ensure labels are treated as categories
            tickmode="array", 
            tickvals=[str(year) for year in range(2005, 2025)],  # Explicitly set all years
            ticktext=[str(year) for year in range(2005, 2025)],  
            tickangle=-45  # Rotates x-axis labels 90 degrees
        ),
        bargap=0.1  # Reduces space between bars
    )

    return fig

init_polarity_mean_years_bar = create_polarity_mean_years_bar(theme)

###################################
# MOST FREQUENT WORDS/BIGRAMS/TRIGRAMS

bigram_data = pd.read_csv('data/Billboard_lyrics/Billboard_Bigramms_and_Trigramms/bigram_data.csv')
trigram_data = pd.read_csv('data/Billboard_lyrics/Billboard_Bigramms_and_Trigramms/trigram_data.csv')

bigram_df = pd.DataFrame(data = bigram_data)
bigram_df['Bigram'] = bigram_df['Bigram'].apply(lambda x: ' '.join(eval(x)))
trigram_df = pd.DataFrame(data = trigram_data)
trigram_df['Trigram'] = trigram_df['Trigram'].apply(lambda x: ' '.join(eval(x)))

def create_word_frequency_bigram_trigram(mode, theme):
    if mode == 'bigram':
        df = bigram_df
        fig = px.bar(bigram_df, x='Bigram', y='Frequency')
    else:
        df = trigram_df
        fig = px.bar(trigram_df, x='Trigram', y='Frequency')

    fig.update_layout(
        xaxis_title = 'Phrase',
        yaxis_title = 'Frequency',
        autosize = True,
        xaxis = dict(tickangle=-45),
        yaxis = dict(
            tickmode = 'linear',
            dtick = max(df['Frequency'].max() // 10, 1)),
        height = 600,
        template = theme,
    )

    return fig

init_word_frequency_chart = create_word_frequency_bigram_trigram('bigram', theme)

###################################
# WORD CLOUD

# Colormap for light theme.
blues_cm = mpl.colormaps['Blues']
blues_light_cm = ListedColormap(blues_cm(np.linspace(0.50, 1.00, 128)))
blues_dark_cm = ListedColormap(blues_cm(np.linspace(0.00, 0.80, 204)))

def create_wordcloud(bgcolor, text = all_lyrics):
    wordcloud = WordCloud(
        width = 1500,
        height = 535,
        background_color = bgcolor,
        #background_color = '#ffffff',
        stopwords = STOP_WORDS
    ).generate(text)
    if bgcolor == '#d9e3f1':
        wordcloud.recolor(colormap = blues_light_cm)
    else:
        wordcloud.recolor(colormap = blues_dark_cm)

    img = wordcloud.to_image()

    buffer = BytesIO()
    img.save(buffer, format = 'PNG')
    buffer.seek(0)
    encoded_img = base64.b64encode(buffer.getvalue()).decode()

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=f'data:image/png;base64,{encoded_img}',
            x = 0,
            y = 1,
            xref = 'paper',
            yref = 'paper',
            sizex = 1,
            sizey = 1,
            xanchor = 'left',
            yanchor = 'top',
            layer = 'below'
        )
    )
    fig.update_layout(
        autosize = True,
        #width = 1500 * 0.843,
        #height = 450 * 0.843,
        margin = dict(l=0, r=0, t=0, b=0),
        xaxis = dict(visible = False),
        yaxis = dict(visible = False)
    )
    return fig

init_wordcloud_img = create_wordcloud(bg_color, all_lyrics)

###################################
# HTML ELEMENTS
###################################

# Define your html elements such as dbc.Container or dbc.Sliders here.
# Any related callbacks need to be defined in app.py
# Name these elements precisely and plug them into the layout below.

###################################
# WORDCLOUD

# Wordcloud Text
wordcloud_text = dbc.Container(
    '''The most frequently used words in song lyrics provide insight into
    lyrics trends. This wordcloud displays the most common words appearing in
    songtexts over all the years we've analyzed. Many of these words are simple 
    exclamations such as "oh", "yeah" and "la" which serve rhythmic rather than 
    semantic purposes as frequently seen in lyrics of rap and hip-hop music. 
    Other words like "love", "baby" and "life" are more common in pop 
    songwriting. Interestingly, the presence of words with negative polarity 
    values such as "fuck" and "bitch" suggests that lyrics contain explicit 
    and aggressive language. This is further analyzed in the polarity-section 
    further down.''', class_name = 'mb-2'
)

# Wordcloud Wrapper object
wordcloud = dbc.Container([
    html.H3('Wordcloud'),
    wordcloud_text,
    dcc.Graph(figure = init_wordcloud_img,
              id = 'wordcloud',
              className='d-grid d-md-block mx-auto')
], class_name='mt-3 mb-5')

###################################
# POLARITY

polarity_years_text = dbc.Container([
    html.H3('Polarity'),
    html.P('''Song lyrics often reflect emotions and moods of their time. By extracting
     them using the Genius API and analyzing their polarity over the years with 
    TextBlob, we can identify cultural trends about how the language in songs 
    becomes positively or negatively charged. The first plot shows the average 
    polarity for each year. From 2005 to 2010 it increased, reaching its peak 
    around 2010 meaning the lyrics became more positive during this time. 
    The lowest values appear between 2017 and 2020. \n
    The second plot in this section contains more detail and puts the mean 
    values into perspective by providing absolute word frequencies for different 
    polarities for each year.''')], class_name = 'mb-2'
)

polarity_years_chart = dbc.Container([
    html.H4('Polarity distribution per year'),
    dcc.Graph(
        id = 'polarity-year-chart',
        figure = init_polarity_years_chart
    )
], class_name = 'mt-5')

polarity_avg_years_chart = dbc.Container([
    html.H4('Polarity mean per year'),
    dcc.Graph(
        id = 'polarity-mean-year-chart',
        figure = init_polarity_mean_years_bar
    )
])

polarity_wrapper = dbc.Container([
    polarity_years_text,
    polarity_avg_years_chart,
    polarity_years_chart
], class_name = 'mb-5')

###################################
# BIGRAM TRIGRAM CHART

bigram_trigram_text = dbc.Container(
    '''
    Lyrics oftentimes are what makes listeners relate to a song. We've looked 
    into the lyrics of the Top 100 songs and used the nltk package to identify 
    the most frequently used phrases.
    '''
)

bigram_trigram_radio = dbc.RadioItems(
    id = 'bigram-trigram-radio',
    options = [
        {'label': 'Show digrams', 'value': 'bigram'},
        {'label': 'Show trigrams', 'value': 'trigram'}
    ],
    value = 'bigram',
    inline = True
)

bigram_trigram_controls = dbc.Row([
    dbc.Col(bigram_trigram_radio, width = 'auto'),
    dbc.Col(class_name = 'fa-regular fa-circle-question',
            id = 'bigram-trigram-radio-info',
            style = {'cursor': 'pointer'},
            width = 'auto'
        ),
    dbc.Col(
        dbc.Tooltip(
            'Changes the viewing mode to either bigram or trigram. Bigram'
            'contains the top 20 most frequent two-word phrases, trigram the'
            'top 20 most frequent three-word phrases.',
            target = 'bigram-trigram-radio-info',
            placement = 'right'
        )
    )
])
bigram_trigram_info_text = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col(class_name='fa-regular fa-lightbulb', width = 'auto'),
            dbc.Col(html.H5('info', className = 'card-title align-top'))
        ]),
        html.P(
            '''
            Some of the Bigrams do not represent actual lyrics, but annotations
            that signal who of several artists appearing in a feature or 
            collaboration project is currently singing their part. Future work
            should be done on identifying when an Artist's name is part of a
            song and when it is just an annotation meant for the reader of lyrics.
            ''', className = 'mb-0'
        )], class_name='p-2 p2-5 ps-5'
    )
    ], color = 'secondary', class_name='mb-4 p-2'
)

bigram_trigram_barchart = dbc.Container([
    html.H3('Top 20 most frequent phrases'),
    bigram_trigram_text,
    bigram_trigram_info_text,
    bigram_trigram_controls,
    dcc.Graph(
        id = 'bigram-trigram-barchart',
        figure = init_word_frequency_chart
    )
], class_name = 'mb-5')

###################################
# MAIN LAYOUT
###################################

# Layout elements can be plugged in here.
# Don't change the name from layout to anything else. Dash page
# registry needs this attribute to properly load the content.

layout = html.Div([ 
    heading,
    main_content,
    wordcloud,
    bigram_trigram_barchart,
    polarity_wrapper,
], className = 'mb-5')
