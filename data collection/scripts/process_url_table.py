#!/usr/bin/env python

import csv
from extract_chords_from_url import get_chords
from numerize_chords import convert_song_to_harmony
from time import sleep
from random import randint

def process_csv(path: str) -> None:
    results = []
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        for song in songs:
            song_name = song['Title']
            artist_name = song['Artist']
            tab_url = song['UG_link']

            # Add random delay or whatever so that we don't get blacklisted...
            # This is very very important!
            sleep(randint(1,4))

            chords = get_chords(tab_url)
            if chords is None:
                print(f"\"{song_name}\" by {artist_name} => {None}")
                results.append({
                    'Title': song_name,
                    'Artist': artist_name,
                    'UG_link': tab_url if tab_url else 'not found',
                    'Harmony': None
                })
            else:
                harmony = convert_song_to_harmony(chords)
                print(f"\"{song_name}\" by {artist_name} => {harmony}")
                results.append({
                    'Title': song_name,
                    'Artist': artist_name,
                    'UG_link': tab_url if tab_url else 'not found',
                    'Harmony': harmony
                })
    print(results)


#process_csv('./billboard_2024_chords.csv')

