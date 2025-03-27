import pandas as pd
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Neccesary nltk downloads for the codes
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

# initialising Stop Words and Lemmatizer
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# List of unwanted words in the preproccesed lyrics file
unwanted_tokens = {"ain't", "'d", "'s", "'m", "'ll", "'ve", "'re","n't", "``", "''", "ai", "’", "'"}

# Function to Preproccess lyrics
# Below function has been modified with the help of Chatgpt
def preprocess_lyrics(lyrics):
    if pd.isna(lyrics):  # if lyrics are missing return as an empty space
        return ""
    
    lyrics = lyrics.lower()  # put everything in lowercase
    words = word_tokenize(lyrics)  # tokenize

    # Removing unwanted Words and lemmatize
    processed_words = [
        lemmatizer.lemmatize(word) for word in words
        if word not in stop_words and word not in string.punctuation and word not in unwanted_tokens
    ]

    return " ".join(processed_words)  # convert List to string

# reading file
file_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\Billboard_Lyrics_Text\billboard_2013_Lyrics_text.csv"  
df = pd.read_csv(file_path)

#apply to the lyrics collumn
df["Lyrics"] = df["Lyrics"].apply(preprocess_lyrics)


processed_file_path = "billboard_2013_Lyrics_preprocessed.csv"
df.to_csv(processed_file_path, index=False)

print(f"Preprocessing abgeschlossen! Datei gespeichert als: {processed_file_path}")
