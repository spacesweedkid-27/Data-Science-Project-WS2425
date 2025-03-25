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
from collections import Counter
from nltk.util import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import glob
import os
import re

dash.register_page(__name__)

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


### POLARITY CHART INTERACTIVE ###

### MOST FREQUENT WORDS/BIGRAMMS/TRIGRAMMS ###


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
### WORD CLOUDS ###

# Create Word Cloud
# Word Cloud Generation Function
def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color="white", stopwords=STOP_WORDS).generate(text)
    img = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    return "data:image/png;base64," + base64.b64encode(img.read()).decode()

wordcloud_img = generate_wordcloud(all_lyrics)


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
word_cloud = html.Img(src=wordcloud_img, style={"width": "100%", "height": "auto"})

###################################
# MAIN LAYOUT
###################################

# Layout elements can be plugged in here.
# Don't change the name from layout to anything else. Dash page
# registry needs this attribute to properly load the content.
# Layout of the Lyrics page
layout = html.Div([ 
    # Store lyrics data for use in callbacks
    dcc.Store(id='lyrics-store', data=all_lyrics),  # Store data here
    
    heading,
    main_content,
    screaming,
    
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
        word_cloud  # Assuming word_cloud is defined
    ])
])