import csv
import requests
from bs4 import BeautifulSoup
import re
import os

# Genius API Token
GENIUS_API_TOKEN = 'XEO7v-2JGWVsHSUXV8HC7n6S7iXY8Uh_BMoqdYBDimTttVOAquc1EUT0z_DcbL9U'

# Function to retrieve artist information
def request_artist_info(artist_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search'
    params = {'q': artist_name, 'per_page': 10, 'page': page}
    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    return response

# Function to retrieve song URLs
def request_song_url(artist_name, song_cap):
    page = 1
    songs = []
    while True:
        response = request_artist_info(artist_name, page)
        if response is None:
            break
        json_data = response.json()
        if 'response' not in json_data or 'hits' not in json_data['response']:
            print("Error: 'response' or 'hits' key not found in the response data")
            break
        song_info = []
        for hit in json_data['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info.append(hit)
        for song in song_info:
            if len(songs) < song_cap:
                url = song['result']['url']
                songs.append(url)
        if len(songs) == song_cap:
            break
        else:
            page += 1
    return songs

# Function to scrape lyrics from a Genius song URL
def scrape_song_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics_divs = html.find_all('div', attrs={'data-lyrics-container': 'true'})
    if not lyrics_divs:
        print(f"Could not find lyrics for {url}")
        return ""
    lyrics = '\n'.join([div.get_text(separator="\n") for div in lyrics_divs])
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
    return lyrics

# Function to write lyrics to CSV file
def write_lyrics_to_csv(input_csv, output_csv):
    # Read the input CSV file
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Lyrics']  # Adding Lyrics column
        rows = list(reader)
    
    # Open the output CSV file for writing
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Loop through each song in the input CSV
        for row in rows:
            artist_name = row['Artist']
            song_title = row['Title']
            lyrics_url = row['Lyrics_URL']
            
            # Scrape lyrics from Genius URL
            lyrics = scrape_song_lyrics(lyrics_url)

            # Add lyrics to the row and write it to the output CSV
            row['Lyrics'] = lyrics
            writer.writerow(row)

    print(f'Lyrics have been added to {output_csv}')

# Calling the function with the original CSV file and the desired output file
input_csv = r'C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\billboard_2005_with_lyrics.csv'
output_csv = 'billboard_2005_with_lyrics_and_lyrics.csv'
write_lyrics_to_csv(input_csv, output_csv)
