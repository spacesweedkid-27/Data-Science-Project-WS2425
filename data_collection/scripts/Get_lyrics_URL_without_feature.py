import requests
import pandas as pd
import time

#Genius APi token and URL used
GENIUS_API_TOKEN = "XEO7v-2JGWVsHSUXV8HC7n6S7iXY8Uh_BMoqdYBDimTttVOAquc1EUT0z_DcbL9U"
GENIUS_API_URL = "https://api.genius.com"

# reading the csv file
file_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\raw\billboard_2013.csv"  # Stelle sicher, dass die Datei im selben Verzeichnis ist
df = pd.read_csv(file_path)

# Clean artist name collumn for easier api handling
def clean_artist_name(artist):
    # removed "featuring", "and", "feat." and any text that follows
    artist_cleaned = artist.lower()
    

    if "featuring" in artist_cleaned:
        artist_cleaned = artist_cleaned.split("featuring")[0].strip()
    elif "feat." in artist_cleaned:
        artist_cleaned = artist_cleaned.split("feat.")[0].strip()
    elif "and" in artist_cleaned:
        artist_cleaned = artist_cleaned.split("and")[0].strip()

    # Removing text inside parentheses or slashes
    artist_cleaned = artist_cleaned.split("(")[0].strip()
    artist_cleaned = artist_cleaned.split("/")[0].strip()
    

    return artist_cleaned.title()

# Call Song-URLs
#Below function has been modified with the help of Chatgpt
def get_song_lyrics_url(title, artist):
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = f"{GENIUS_API_URL}/search"
    
    # Clean artist name
    artist_cleaned = clean_artist_name(artist)
    
    # generate a search term
    params = {"q": f"{title} {artist_cleaned}"}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        return None

    try:
        song_info = response.json()["response"]["hits"]
        if not song_info:
            return None

        # Use the first hit to the generated term
        song_url = song_info[0]["result"]["url"]
        return song_url
    except:
        return None

# Add a new collumn for the Lyrics URL
df["Lyrics_URL"] = df.apply(lambda row: get_song_lyrics_url(row["Title"], row["Artist"]), axis=1)


new_file_path = "billboard_2013_lyrics_URL.csv"
df.to_csv(new_file_path, index=False)


