import csv
import random
import requests
import re

def search(song, artist):
    query = f'"{song}" "{artist}'
    url = f'https://ultimate-guitar.com/search.php?search_type=title&value={query} chords'

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
    
    '''Ultimate Guitar hides the links within JSON structures on load, so instead of
    accessing them through their a href tag we'll need to look for the appropriate
    link structure in the returned JSON. Currently this works under the assumption
    that the first link found is always a "chords"-tab, as this is the most common
    search-result, but especially for older songs this might vary. A solution might
    be to also check whether "chords" is somewhere within the link, as it usually is,
    but I can't be 100% sure about this right now. The next steps in the processing-workflow
    will reveal if I need to refine a couple of things.'''

    match = re.search(r'https://tabs\.ultimate-guitar\.com/tab/[^&]*', response.text)

    if match:
        return match.group(0)
        
    return None

def getUGlinks(input, output):
    # read chart csv, copy info to new csv and add link
    with open(input, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        # results list to buffer title, artist and links
        results = []
        for song in songs:
            song_name = song["Title"]
            artist_name = song["Artist(s)"]

            print(f'Searching for {song_name} by {artist_name}')
            '''currently it looks like UG doesn't ban automatic queries as quickly,
            but I haven't found reliable information about that yet and have only tested
            with a small amount of queries (5-7 per test run), which might also be
            the reason I haven't been banned yet. A sleep timer might be a solution
            but for testing it just took too long.'''
            #time.sleep(random.randint(10,100)) # randomly sleep between queries to not get locked out
            tab_url = search(song_name, artist_name)

            results.append({
                "Title": song_name,
                "Artist": artist_name,
                "UG_link": tab_url if tab_url else "not found"
            })

        # write result into new csv
        with open(output, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Title", "Artist", "UG_link"]
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f'results saved for {output}')


# it might be useful to add automation to this process as well
getUGlinks("billboard_2024.csv", "billboard_2024_chords.csv")
