import csv
import sys
import re
import unicodedata
import getchords

# example call for this function (while being in root directory of venv):
# python3 "data collection/scripts/clean_urls.py" "data/chords/billboard_2024.csv" "data/chords/logs/billboard_2024.csv"

def compare_urls():
    ''' Commandline-tool that compares found urls to artist-names and
    songtitles. Automatically parses the names into url-format for comparison.
    Prints data in the commandline whenever differing result is found. Url can
    then be accepted or disregarded manually by typing "y" or "n" in the
    commandline. Logs changes in log file to make it a bit more transparent.
    
    Parameters:
    input_file (str): Valid path to input file that needs to be checked.
    output (str): Valid path to log file that will contain the names of artists
    and songs, as well as the links that have been manually rejected.'''

    input_file = sys.argv[1]
    log = sys.argv[2]

    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        results = [] #  Buffer for chords file.
        changes = [] #  Buffer for log file.

        for song in songs:
            song_title = to_url(song['Title'])
            # print(song_title)
            artist_name = to_url(getchords.remove_featuring(song['Artist']))
            # print(artist_name)
            url = song['UG_link']

            if song_title not in url or artist_name not in url:
                if url != 'not found':
                    print(f'diff in link\nArtist: {song['Artist']}\n' +
                          f'Song: {song['Title']}\nLink: {url}')
                    accept = input('Accept? [y/n]\n')
                    if accept == 'y':
                        results.append({
                            'Title': song['Title'],
                            'Artist': song['Artist'],
                            'UG_link': song['UG_link']
                        })
                    else:
                        results.append({
                            'Title': song['Title'],
                            'Artist': song['Artist'],
                            'UG_link': 'not found'
                        })
                        # A change was made, needs to be logged, so append it to
                        # changes list to save later.
                        changes.append({
                            'Title': song['Title'],
                            'Artist': song['Artist'],
                            'UG_link': song['UG_link']
                        })
                else:
                    results.append({
                            'Title': song['Title'],
                            'Artist': song['Artist'],
                            'UG_link': song['UG_link']
                        })
            else:
                results.append({
                    'Title': song['Title'],
                    'Artist': song['Artist'],
                    'UG_link': song['UG_link']
                })

        with open(input_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Changes rejected urls in chords file.
            fieldnames = ['Title', 'Artist', 'UG_link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f'results saved for {input_file}')

        with open(log, 'w', newline='', encoding='utf-8') as csvfile:
            # Saves changes in log file. Not necessary but interesting to know
            # how many links the scraper got wrong.
            fieldnames = ['Title', 'Artist', 'UG_link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(changes)
        print(f'changes logged in {log}')

def lowercase_name(name):
    ''' Turns whitespaces into '-'. '''
    return name.replace(' ', '-').lower()

def clean_special_characters(str):
    ''' Removes special characters from strings.'''
    str = re.sub('[^A-Za-z0-9 ]+', '', str)
    return str

def remove_accents(str):
    ''' Subsitutes accented characters with their unaccented counterparts.'''
    return ''.join(
        c for c in unicodedata.normalize('NFD', str)
        if unicodedata.category(c) != 'Mn'
    )

def to_url(str):
    ''' Calls all cleaning functions on a passed String.'''
    accentfree_str = remove_accents(str)
    specialcharfree_str = clean_special_characters(accentfree_str)
    cleaned_str = lowercase_name(specialcharfree_str)
    return cleaned_str

compare_urls()

''' Ignore, this is just test data
Title,Artist,UG_link
"""Lose! Control""",Teddy Swims,https://tabs.ultimate-guitar.com/tab/teddy-swims/lose-control-chords-4835888
"""A Bar Song (Tipsy)""",Shaboozey,https://tabs.ultimate-guitar.com/tab/shaboozey/a-bar-song-tipsy-chords-5223882
"""Beautiful Things""",Benson Boone,https://tabs.ultimate-guitar.com/tab/benson-boone/beautiful-things-chords-5110429
"""I Had Some Help""",Post Malone featuring Morgan Wallen,not found
"""Lovin on Me""",Jack Harlow,https://tabs.ultimate-guitar.com/tab/adele/lovin-on-me-chords-5037415
'''