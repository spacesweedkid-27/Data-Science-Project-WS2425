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

# Daten einlesen & Lyrics kombinieren
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

# Alle Jahre zusammenfügen
all_data = pd.concat(dataframes, ignore_index=True)

# Alle Lyrics zu einer Liste zusammenführen
all_lyrics = ' '.join(all_data['Lyrics'].dropna()).lower()  # Alles in Kleinbuchstaben

# Funktion für Wort-, Bigramm-, Trigramm-Häufigkeiten
def get_ngram_frequencies(text, n=1, top_n=20):
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS]  # Stop-Wörter entfernen
    
    if n == 1:
        ngram_list = tokens
    else:
        ngram_list = [ng for ng in ngrams(tokens, n) if len(set(ng)) == n]  # Unterschiedliche Wörter erzwingen
    
    freq = Counter(ngram_list)
    return freq.most_common(top_n)


# Bigramme und Trigramme berechnen
bigram_frequencies = get_ngram_frequencies(all_lyrics, n=2)
trigram_frequencies = get_ngram_frequencies(all_lyrics, n=3)

# Daten für CSV vorbereiten (hier ohne .items())
bigram_data = pd.DataFrame(bigram_frequencies, columns=["Bigram", "Frequency"])
trigram_data = pd.DataFrame(trigram_frequencies, columns=["Trigram", "Frequency"])

# In CSV speichern
bigram_data.to_csv("bigram_data.csv", index=False)
trigram_data.to_csv("trigram_data.csv", index=False)

print("Bigramme und Trigramme wurden erfolgreich gespeichert.")
