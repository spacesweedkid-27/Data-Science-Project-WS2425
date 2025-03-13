import csv
from spotify_api_token import get_token, get_auth_header
from requests import get
import time
import os

def search_for_song_duration(token, artist, title):
    """
    Searches for a song on Spotify and returns its duration in milliseconds.
    
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    
    query = f"q=artist:{artist} track:{title}&type=track&limit=1"
    
    query_url = f"{url}?{query}"

    #Send the GET request to the API
    result = get(query_url, headers=headers)

    if result.status_code != 200:
        print(f"Faulty API-Request: {result.status_code}")
        return None

    json_result = result.json()
    if json_result['tracks']['total'] > 0:
        track = json_result['tracks']['items'][0] 
        return track['duration_ms']  
    else:
        print(f"Not found.")
        return None

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
                results.append({
                    'Title': title,
                    'Artist': artist,
                    'Duration_ms': duration_ms,
                    'Duration_s': round(duration_sec, 2)  
                })

            time.sleep(1)  
    
    return results  


csv_files = [
    "Data-Science-Project-WS2425/data/raw/billboard_2007.csv",
    "Data-Science-Project-WS2425/data/raw/billboard_2008.csv",
    "Data-Science-Project-WS2425/data/raw/billboard_2009.csv",
    "Data-Science-Project-WS2425/data/raw/billboard_20010.csv",
    "Data-Science-Project-WS2425/data/raw/billboard_20011.csv",
    
    #To-Do: Add other files
]


for file in csv_files:
    print(f"Processed file: {file}...")
    

    results = process_csv(file)
    
   
    output_filename = f"/Data-Science-Project-WS2425/data/raw{os.path.basename(file).replace('.csv', '_with_duration.csv')}"
    
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Artist', 'Duration_ms', 'Duration_s']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved in: {output_filename}")
