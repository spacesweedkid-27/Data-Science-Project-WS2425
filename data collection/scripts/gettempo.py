import csv
import random
import requests
from bs4 import BeautifulSoup
import os
import time

# Funktion zum Entfernen von 'featuring' oder 'feat.' im Künstlernamen
def remove_featuring(artist):
    """
    Entfernt 'featuring', 'feat.', oder 'feat' aus dem Künstlernamen.
    Gibt nur den ersten Künstler zurück.
    """
    if "featuring" in artist.lower():
        return artist.split("featuring")[0].strip()
    elif "feat." in artist.lower():
        return artist.split("feat.")[0].strip()
    elif "feat" in artist.lower():
        return artist.split("feat")[0].strip()
    return artist

# Funktion zum Ersetzen von Zahlen und Sonderzeichen im Songtitel
def replace_numbers_and_special_chars(text):
    num_dict = {
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "0": "zero",
        ",": "",  # Entferne Komma
        "&": "and",  # Ersetze '&' durch 'and'
        ".": "",  # Entferne Punkte  "Mr." -> "mr"
        "'": "",  # Entferne Apostrophen nur für Songtitel und Künstlernamen
        "don't": "dont",  # Ersetze don't in Songtiteln
        "I'm": "i-m",  # Ersetze I'm in Songtiteln
    }

    for key, value in num_dict.items():
        text = text.replace(key, value)
    
    # Apostrophen nur bei "I'm" behandeln und den Bindestrich einfügen
    text = text.replace("I'm", "i-m")
    
    return text


def get_song_tempo(artist, song):
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
        ])
    }

    # Entferne "featuring", "feat." und "feat" aus dem Künstlernamen
    artist = remove_featuring(artist).replace(' ', '-').lower()  # Künstlername
    song = song.strip()  # Songtitel ohne Veränderung
    song = replace_numbers_and_special_chars(song).replace(' ', '-').lower()  # Songtitel

    
    url = f'https://songbpm.com/@{artist}/{song}'
    
    print(f"Versuche URL: {url}")  
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")

    
    tempo = [i.text for i in soup.select("span.bg-red-100, span[style='display-style']")]

    if tempo:
        return tempo[0]  # Gib das erste Tempo zurück
    else:
        print(f"Tempo für {artist} - {song} konnte nicht gefunden werden.")
        return None


def process_csv(path: str) -> list:
    results = []

    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        for song in songs:
            artist = song['Artist']
            title = song['Title']
            print(f"Searching for BPM: {artist} - {title}")
            
            
            tempo = get_song_tempo(artist, title)
            
            
            if tempo:
                results.append({
                    'Title': title,
                    'Artist': artist,
                    'Tempo': tempo
                })
            
            time.sleep(1.4) 
    
    return results


csv_files = [
    "..",
    
]

for file in csv_files:
    print(f"Processing file: {file}...")
    
    results = process_csv(file)
    
    output_filename = f"../{os.path.basename(file).replace('.csv', '_with_bpm.csv')}"
    
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Artist', 'Tempo']  
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved in: {output_filename}")
