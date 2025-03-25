import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import nltk
from dash_bootstrap_templates import load_figure_template
from collections import Counter
from nltk.util import ngrams
from wordcloud import WordCloud
import base64
from io import BytesIO
import glob
import os
import re
import random
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

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
STOP_WORDS = {"wan", "na", "ta", "ca"}

###################################
# POLARITY CHART INTERACTIVE

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


blues_cm = mpl.colormaps['Blues']
blues_light_cm = ListedColormap(blues_cm(np.linspace(0.50, 1.00, 128)))

def create_wordcloud(bgcolor, text = all_lyrics):
    wordcloud = WordCloud(
        width = 800,
        height = 400,
        background_color = bgcolor,
        stopwords = STOP_WORDS
    ).generate(text)
    if bgcolor == '#d9e3f1':
        wordcloud.recolor(colormap = blues_light_cm)
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
    dcc.Graph(figure = init_wordcloud_img, id = 'wordcloud', className='d-grid d-md-block mx-auto')
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

###################################
# MAIN LAYOUT
###################################

# Layout elements can be plugged in here.
# Don't change the name from layout to anything else. Dash page
# registry needs this attribute to properly load the content.
# Layout of the Lyrics page
layout = html.Div([ 
    # Store lyrics data for use in callbacks
    #dcc.Store(id='lyrics-store', data=all_lyrics),  # Store data here
    
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
