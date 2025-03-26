import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from textblob import TextBlob
import numpy as np
import nltk
from dash_bootstrap_templates import load_figure_template
from collections import Counter
from nltk.util import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import glob
import os
import re
import random

dash.register_page(__name__)

load_figure_template('morph')
theme = 'morph' #  Initial theme that needs to be passed to graphs on load
bg_color = '#212529'

heading = dbc.Container('We got some information about tempo here')
main_content = dbc.Container('Some information about this project goes here. '
'This content answers questions about what data sources we used, how the data '
'was processed and what assumptions were made. Whilest this information not '
'being listed in the official requirements provided by CAU, it still holds a lot'
'of value from a scientific standpoint.')
screaming = dbc.Container('NEVER GONNA GIVE YOU UP, NEVER GONNA LET YOU DOWN, '
'NEVER GONNA RUN AROUND AND DESERT YOU. NEVER GONNA MAKE YOU CRY, NEVER GONNA '
'SAY GOODBYE, NEVER GONNA TELL A LIE AND HURT YOU!')

# Verzeichnis und CSV-Dateien laden
folder_path = "data/Billboard_lyrics/BillBoard_Lyrics_preprocessed"
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
STOP_WORDS = {"wan", "na", "ta", "ca"}

###################################
# POLARITY CHART INTERACTIVE
if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)
else:
    raise ValueError("Keine gültigen CSV-Dateien gefunden.")

# Funktion zur Berechnung der Wortpolarität
def get_word_polarity(text):
    if isinstance(text, str):  
        words = text.split()
        polarities = [TextBlob(word).sentiment.polarity for word in words]
        return polarities
    return []

all_data['Polarity'] = all_data['Lyrics'].apply(get_word_polarity)

# Daten für die Visualisierung vorbereiten
years = list(range(2005, 2025))
polarities_by_year = {year: [] for year in years}
mean_polarities = {}

for year in years:
    yearly_data = all_data[all_data['Year'] == year]
    if not yearly_data.empty:
        all_polarities = [p for sublist in yearly_data['Polarity'] for p in sublist]
        polarities_by_year[year] = all_polarities
        mean_polarities[year] = np.mean(all_polarities) if all_polarities else 0  # Durchschnitt berechnen
    else:
        mean_polarities[year] = 0

#Interaktive Visualisierung mit Optimierung
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
        name=f'Negativ ({year})',
        marker_color='red',
        opacity=0.7,
        visible=True if year == 2005 else False
    ))

    fig.add_trace(go.Histogram(
        x=positive,
        name=f'Positiv ({year})',
        marker_color='blue',
        opacity=0.7,
        visible=True if year == 2005 else False
    ))

    fig.add_trace(go.Histogram(
        x=neutral,
        name=f'Neutral ({year})',
        marker_color='gray',
        opacity=0.5,
        visible=True if year == 2005 else False
    ))

    # Durchschnittliche Polarität als dünne vertikale Linie 
    fig.add_trace(go.Scatter(
        x=[mean_polarities[year], mean_polarities[year]],  # Linie bei Durchschnittswert
        y=[1, 10**5],  # Höhe der Linie (angepasst für logarithmische Skalierung)
        mode="lines",
        line=dict(color="orange", width=2, dash="dash"),  # Farbe: Orange, Dünn, Gestrichelt
        name=f'Durchschnitt ({year})',
        visible=True if year == 2005 else False
    ))

#Korrekte Slider-Definition 
steps = []
for i, year in enumerate(years):
    step = dict(
        method="update",
        args=[{"visible": [j // 4 == i for j in range(len(years) * 4)]}],
        label=str(year)
    )
    steps.append(step)

fig.update_layout(
    title="Verteilung der Wortpolaritäten in Songtexten (2005–2024)",
    xaxis_title="Polarität",
    yaxis_title="Anzahl der Wörter",
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

###################################
# MOST FREQUENT WORDS/BIGRAMMS/TRIGRAMMS


# Create function for n-gram frequency analysis
def get_ngram_frequencies(text, n=1, top_n=20):
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS]
    
    # For n > 1, filter out n-grams that have repeated words
    if n > 1:
        ngram_list = [ng for ng in ngrams(tokens, n) if len(set(ng)) == n]
    else:
        ngram_list = tokens
    
    freq = Counter(ngram_list)
    return freq.most_common(top_n)

# Define the helper function to generate the word frequency chart
def create_word_frequency_chart(n):
    freq_data = get_ngram_frequencies(all_lyrics, n)
    words, counts = zip(*freq_data)
    words = [" ".join(w) if isinstance(w, tuple) else w for w in words]
    
    # Basic bar chart with Plotly Express
    fig = px.bar(x=words, y=counts, labels={"x": "Words/Phrases", "y": "Frequency"},
                 title=f"Top {len(words)} Most Frequent {'Words' if n==1 else 'Phrases'}",
                 text_auto=True)
    return fig

###################################
# WORD CLOUDS

# Create Word Cloud
# Word Cloud Generation Function
'''def create_wordcloud(text, bgcolor):
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color=bgcolor,
        stopwords=STOP_WORDS).generate(text)
    img = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    return "data:image/png;base64," + base64.b64encode(img.read()).decode()'''

def generate_wordcloud_blue_colors():
    return (f'rgb({random.randint(0,100)},{random.randint(0,100)},{random.randint(100,255)})')

def create_wordcloud(bgcolor, text = all_lyrics):
    wordcloud = WordCloud(
        width = 800,
        height = 400,
        background_color = bgcolor,
        stopwords = STOP_WORDS
    ).generate(text)
    if bgcolor == '#d9e3f1':
        wordcloud.recolor(colormap = 'ocean') # light background
    else:
        wordcloud.recolor(colormap = 'Blues')

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
        width = 800,
        height = 400,
        margin = dict(l=0, r=0, t=0, b=0),
        xaxis = dict(visible = False),
        yaxis = dict(visible = False)
    )
    return fig

init_wordcloud_img = create_wordcloud(bg_color, all_lyrics)

# Wordcloud Wrapper object
wordcloud = dbc.Container([
    html.H3('Wordcloud'),
    html.P('Controls go here'),
    dcc.Graph(figure = init_wordcloud_img, id = 'wordcloud')
], class_name='mt-3')

###################################
# HTML ELEMENTS
###################################

# Define your html elements such as dbc.Container or dbc.Sliders here.
# Any related callbacks need to be defined in app.py
# Name these elements precicesly and plugg them into the layout below.

polarity_chart = dcc.Graph(id="polarity-chart")
ngram_slider = dcc.Slider(
    id="ngram-slider",
    min=1,
    max=3,
    step=1,
    marks={1: "Words", 2: "Bigrams", 3: "Trigrams"},
    value=1,
)
word_frequency_chart = dcc.Graph(id="word-frequency-chart")
'''word_cloud = html.Img(src=init_wordcloud_img,
                      style={"width": "100%", "height": "auto"})'''

###################################
# MAIN LAYOUT
###################################

# Layout elements can be plugged in here.
# Don't change the name from layout to anything else. Dash page
# registry needs this attribute to properly load the content.
# Layout of the Lyrics page

##layout add for polarity 
layout = html.Div([
    html.H1("Analyse der Songtext-Polarität"),
    dcc.Slider(
        id="year_slider",
        min=2005,
        max=2024,
        step=1,
        marks={year: str(year) for year in range(2005, 2025)},
        value=2005
    ),
    dcc.Graph(id="lyrics_graph")
])
#

layout = html.Div([ 
    # Store lyrics data for use in callbacks
    dcc.Store(id='lyrics-store', data=all_lyrics),  # Store data here
    
    heading,
    main_content,
    screaming,

    wordcloud,
    
    # New Section for Lyrics Analysis:
    dbc.Container([
        html.H2("Lyrics Analysis"),
        html.P("This section analyzes song lyrics trends over time."),

        # Polarity Chart
        html.H4("Polarity Analysis"),
        dcc.Graph(id="polarity-chart"),  # The graph will be updated through callback

        # Word Frequency Analysis
        html.H4("Word Frequency Analysis"),
        ngram_slider,  # Slider to control n-gram range
        dcc.Graph(id="word-frequency-chart"),  # Word frequency chart
        
        # Word Cloud
        html.H4("Word Cloud"),
       #word_cloud  # Assuming word_cloud is defined
    ])
])
