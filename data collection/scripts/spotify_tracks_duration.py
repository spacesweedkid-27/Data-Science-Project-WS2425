import csv
from spotify_api_token import get_token, get_auth_header
from requests import get
import time
import os
from cleaning import remove_featuring, replace_and  

def search_for_song_duration(token, artist, title):
    """
    Search for a song on Spotify and return its duration.

    Args:
        token (str): Spotify API authentication token.
        artist (str): Name of the artist.
        title (str): Title of the song.

    Returns:
        int/None: duration in milliseconds, seconds and minutes
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    
    artist_variations = [
        artist,  # The original artist name.
        replace_and(artist),  # The artist name with the "and" replaced.
    ]
    
    # Try with each artist variation to get a more acurate search
    for artist_variant in artist_variations:
        query = f"q=artist:{artist_variant} track:{title}&type=track&limit=1"
        query_url = f"{url}?{query}"
        result = get(query_url, headers=headers)
        
        if result.status_code != 200:
            print(f"Faulty API-Request: {result.status_code}")
            continue
        
        json_result = result.json()
        if json_result['tracks']['total'] > 0:
            track = json_result['tracks']['items'][0]
            return track['duration_ms']
    
    # Try a searching with the cleaned artist name.
    cleaned_artist = remove_featuring(artist)
    if cleaned_artist != artist:
        query = f"q=artist:{cleaned_artist} track:{title}&type=track&limit=1"
        query_url = f"{url}?{query}"
        result = get(query_url, headers=headers)
        
        if result.status_code == 200:
            json_result = result.json()
            if json_result['tracks']['total'] > 0:
                track = json_result['tracks']['items'][0]
                return track['duration_ms']
    
    print(f"Not found: {artist} - {title}")
    return None


# Got this part from preprocessing.py and adjusted it.
# Instead of chords it works with duration.
def process_csv(path: str) -> list:
    
    results = []
    token = get_token()

    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        for song in songs:
            artist = song['Artist']
            title = song['Title']
            print(f"Searching for duration: {artist} - {title}")
            
            duration_ms = search_for_song_duration(token, artist, title)

            if duration_ms is not None:
                duration_sec = duration_ms / 1000
                duration_min = duration_ms / 60000
                results.append({
                    'Title': title,
                    'Artist': artist,
                    'Duration_ms': duration_ms,
                    'Duration_s': round(duration_sec, 2), # Rounding up the numbers.
                    'Duration_min': round(duration_min, 2)
                })

            # Waiting before the next API request to prevent exceeding the API rate limit.
            time.sleep(1.4)  
    
    return results


# Defining a list of input CSV files.
csv_files = [
    "Data-Science-Project-WS2425/data/raw/billboard_2005.csv",
    # Add rest of the files.
]

# Process all the files.
for file in csv_files:
    print(f"Processing file: {file}...")
    
    results = process_csv(file)
    
    output_filename = f"Data-Science-Project-WS2425/data/durations/{os.path.basename(file).replace('.csv', '_with_duration.csv')}"
    

    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:

        fieldnames = ['Title', 'Artist', 'Duration_ms', 'Duration_s', 'Duration_min']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader() # Write the header row.
        writer.writerows(results) # Write the processed songs to the file.
        
    print(f"Results saved in: {output_filename}")