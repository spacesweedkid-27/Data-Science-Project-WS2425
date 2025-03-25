import csv
import random
import requests
from bs4 import BeautifulSoup
import os
import time
import re
import unicodedata


def remove_featuring(artist):
    """
    Remove 'featuring', 'feat.', or 'feat'
    
    from artist name.
    """
    if "featuring" in artist.lower():
        return artist.split("featuring")[0].strip()
    elif "feat." in artist.lower():
        return artist.split("feat.")[0].strip()
    elif "feat" in artist.lower():
        return artist.split("feat")[0].strip()
    return artist

def replace_apostrophes(text):
    """
    Replaces apostophes with a -.
    """
    # Regex for words with apostrophe.
    return re.sub(r"(\w+)'(\w+)", r"\1-\2", text)


def replace_special_characters(text):
    """
    Removes or replaces special characters
    
    and puts into a URL-friendly format.
    """
    # Changes special characters.
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Replaces all special characters with a -.
    text = re.sub(r'[^\w\s-]', '-', text)  
    
    
    text = text.replace(" ", "-").lower()
    
    return text


def replace_numbers_and_special_chars(text):
    """
    Replaces special characters in title.
    """
    num_dict = {
        "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", 
        "6": "six", "7": "seven", "8": "eight", "9": "nine", "0": "zero",
        ",": "", ".": "", "'": "", "(": "", ")": "", "!": "", "&": "-"
    }

    text = replace_apostrophes(text)

    for key, value in num_dict.items():
        text = text.replace(key, value)

    
    # Replace double --.
    text = re.sub(r'--+', '-', text)  
    
    return text

def clean_artist_name(artist):
    """
    Cleans up the artist name.
    Uses remove_featuring, replace_sepcial_character
    and replaces . with a -. 
    """
    
    artist = remove_featuring(artist)

    # Remove the "and".
    if " and " in artist.lower():
        artist = artist.split(" and ")[0].strip()

    artist = replace_special_characters(artist)
    
    
    artist = re.sub(r'\.','-', artist)
    
    
    artist = re.sub(r'--+', '-', artist)
    
    return artist

def get_song_tempo(artist, song):
    """
    Looksup the tempo of a song using songbpm.com.
    
    Args:
        artist (str): Artist name
        song (str): song title

    Returns:
        str: BPM, if found, else "NOT FOUND".
    """
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
        ])
    }

    # Cleans up artist name and song title
    clean_artist = clean_artist_name(artist).replace(' ', '-').lower()
    clean_song = replace_numbers_and_special_chars(song).replace(' ', '-').lower()

    url = f'https://songbpm.com/@{clean_artist}/{clean_song}'
    
    print(f"Trying URL: {url}")  
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tempo = [i.text for i in soup.select("span.bg-red-100, span[style='display-style']")]
        if tempo:
            return tempo[0]  # Returns tempo
    
    print(f"404 Error: {response.status_code} - Not Found, versuche 'don-t' Version...")

    modified_song = replace_numbers_and_special_chars(clean_song.replace("don't", "don-t"))
    print(f"Trying modified song title with 'don-t': {modified_song}")
    
    url = f'https://songbpm.com/@{clean_artist}/{modified_song}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tempo = [i.text for i in soup.select("span.bg-red-100, span[style='display-style']")]
        if tempo:
            return tempo[0]

    return "NOT FOUND"

def clean_title(title):
    """
    Removes ".
    """
    return title.strip('"')


# Got this part from preprocessing.py and adjusted it.
def process_csv(path: str) -> list:
    
    results = []

    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        for song in songs:
            artist = song['Artist']
            title = clean_title(song['Title'])
            print(f"Searching for BPM: {artist} - {title}")
            
            tempo = get_song_tempo(artist, title)
            
            
            result = song.copy()
            result['Tempo'] = tempo
            results.append(result)
            
            time.sleep(1.4)  
    
    return results



# Defining a list of input CSV files.
csv_files = [
    "..",

    
    
]

for file in csv_files:
    print(f"Processing file: {file}...")
    
    results = process_csv(file)
    
    output_filename = f"../{os.path.basename(file).replace('.csv', '_with_bpm.csv')}"
    
    # Get all fieldnames from the first result (which should have all original columns and Tempo)
    if results:
        fieldnames = list(results[0].keys())
    else:
        fieldnames = ['No.', 'Title', 'Artist', 'Tempo']  # Fallback if no results
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved in: {output_filename}")
