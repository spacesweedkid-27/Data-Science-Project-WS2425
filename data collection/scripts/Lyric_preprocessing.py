import pandas as pd
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Notwendige NLTK-Ressourcen herunterladen (falls noch nicht geschehen)
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

# Initialisieren von Stopwords und Lemmatizer
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# Liste von unerwünschten Tokens nach der Lemmatisierung
unwanted_tokens = {"ain't", "'d", "'s", "'m", "'ll", "'ve", "'re","n't", "``", "''", "ai", "’", "'"}

# Funktion zur Vorverarbeitung der Lyrics
def preprocess_lyrics(lyrics):
    if pd.isna(lyrics):  # Falls Lyrics fehlen, leere Zeichenkette zurückgeben
        return ""
    
    lyrics = lyrics.lower()  # In Kleinbuchstaben umwandeln
    words = word_tokenize(lyrics)  # Tokenisierung

    # Lemmatisierung + Entfernen von Stopwords, Satzzeichen und unerwünschten Tokens
    processed_words = [
        lemmatizer.lemmatize(word) for word in words
        if word not in stop_words and word not in string.punctuation and word not in unwanted_tokens
    ]

    return " ".join(processed_words)  # Liste in String umwandeln

# Datei einlesen 
file_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\Billboard_Lyrics_Text\billboard_2023_Lyrics_text.csv"  
df = pd.read_csv(file_path)

# Preprocessing auf die "Lyrics"-Spalte anwenden
df["Lyrics"] = df["Lyrics"].apply(preprocess_lyrics)

# Neue Datei speichern
processed_file_path = "billboard_2023_Lyrics_preprocessed.csv"
df.to_csv(processed_file_path, index=False)

print(f"Preprocessing abgeschlossen! Datei gespeichert als: {processed_file_path}")
