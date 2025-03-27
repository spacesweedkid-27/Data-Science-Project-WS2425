import requests
import pandas as pd
import time


### Was improved and replaced by the Get_Lyrics_URL.py since the features stopped the code from working ###
# Genius API Token
GENIUS_API_TOKEN = "XEO7v-2JGWVsHSUXV8HC7n6S7iXY8Uh_BMoqdYBDimTttVOAquc1EUT0z_DcbL9U"
GENIUS_API_URL = "https://api.genius.com"


file_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\raw\billboard_2024.csv"  # Stelle sicher, dass die Datei im selben Verzeichnis ist
df = pd.read_csv(file_path)

# Fetch Song ULR
def get_song_lyrics_url(title, artist):
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = f"{GENIUS_API_URL}/search"
    params = {"q": f"{title} {artist}"}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        return None

    try:
        song_info = response.json()["response"]["hits"]
        if not song_info:
            return None

        # Use first search hit
        song_url = song_info[0]["result"]["url"]
        return song_url
    except:
        return None

#new collumn for lyircs
df["Lyrics_URL"] = df.apply(lambda row: get_song_lyrics_url(row["Title"], row["Artist"]), axis=1)


new_file_path = "billboard_2024_lyrics_URL.csv"
df.to_csv(new_file_path, index=False)

print(f"Neue Datei mit Lyrics-URLs gespeichert als {new_file_path}")
