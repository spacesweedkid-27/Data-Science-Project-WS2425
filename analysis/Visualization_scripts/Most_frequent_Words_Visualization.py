import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import glob
import os
import re
from collections import Counter
from nltk.util import ngrams
import nltk
nltk.download('punkt')


STOP_WORDS = {"wan", "na", "ta", "ca"}  # Wörter, die ignoriert werden sollen


folder_path =  r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\BillBoard_Lyrics_preprocessed"
file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

#Daten einlesen & Lyrics kombinieren
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

#Alle Jahre zusammenfügen
all_data = pd.concat(dataframes, ignore_index=True)

#Alle Lyrics zu einer Liste zusammenführen
all_lyrics = ' '.join(all_data['Lyrics'].dropna()).lower()  # Alles in Kleinbuchstaben

#Funktion für Wort-, Bigramm-, Trigramm-Häufigkeiten
def get_ngram_frequencies(text, n=1, top_n=20):
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS]  # Stop-Wörter entfernen
    
    if n == 1:
        ngram_list = tokens
    else:
        ngram_list = [ng for ng in ngrams(tokens, n) if len(set(ng)) == n]  # Unterschiedliche Wörter erzwingen
    
    freq = Counter(ngram_list)
    return freq.most_common(top_n)

#Dash App erstellen
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Most Frequent Words in Billboard Lyrics"),
    dcc.Slider(
        id='ngram-slider',
        min=1,
        max=3,
        step=1,
        value=1,
        marks={1: 'Words', 2: 'Bigrams', 3: 'Trigrams'}
    ),
    dcc.Graph(id='word-frequency-chart')
])

#Callback-Funktion für interaktive Visualisierung
@app.callback(
    Output('word-frequency-chart', 'figure'),
    Input('ngram-slider', 'value')
)
def update_chart(n):
    freq_data = get_ngram_frequencies(all_lyrics, n)
    words, counts = zip(*freq_data)
    words = [' '.join(w) if isinstance(w, tuple) else w for w in words]
    
    fig = px.bar(x=words, y=counts, labels={'x': 'Words/Phrases', 'y': 'Frequency'},
                 title=f"Top {len(words)} Most Frequent {'Words' if n==1 else 'Phrases'}",
                 text_auto=True)
    return fig

# Server starten
if __name__ == '__main__':
    app.run(debug=True)
