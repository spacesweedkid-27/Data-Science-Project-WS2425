import csv
import random
import requests
from bs4 import BeautifulSoup
import re

# not optimal, google quickly blocks
def google_search(song, artist):
    query = f'site:ultimate-guitar.com "{song}" "{artist} chords'
    url = f'https://google.com/search?q={query}'

    # maybe this helps with getting ip-banned?
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0"
        ])
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'failed to fetch search results for {song} by {artist}')
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")

    # get first valid ultimate-guitar link (publicly accessible, must be chords)
    for link in soup.find_all("a", href=True):
        href = link["href"]

        match = re.search(r"/url\?q=(https://tabs.ultimate-guitar.com/[\S]+)&", href)
        if match:
            tab_url = match.group(1)
            # make sure it's not a pro tab (pro tabs usually have /pro/ in their url)
            if "/pro/" not in tab_url:
                return tab_url

def getUGlinks(input, output):
    # read chart csv, copy info to new csv and add link
    with open(input, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        results = []
        for song in songs:
            song_name = song["Title"]
            artist_name = song["Artist(s)"]

            print(f'Searching for {song_name} by {artist_name}')
            tab_url = google_search(song_name, artist_name)

            results.append({
                "Title": song_name,
                "Artist": artist_name,
                "UG_link": tab_url if tab_url else "not found"
            })

        with open(output, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Title", "Artist", "UG_link"]
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f'results saved for {output}')

print(google_search("Lose Control", "Teddy Swims"))
print(google_search("Someone Like You", "Adele"))

getUGlinks("billboard_2024.csv", "billboard_2024_chords.csv")
