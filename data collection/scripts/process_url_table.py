#!/usr/bin/env python

import csv
from extract_chords_from_url import get_chords
from numerize_chords import convert_song_to_harmony
from process_harmonies import identify_main_harmony_2
from time import sleep
from random import randint


def process_csv_to_chords(input_path: str, output_path: str) -> None:
    """Takes in a path to a csv in Title|Artist|UG_link-format and writes to
       the output path a csv in format Title|Artist|Chords. If there is no
       Url or the URL is broken/unusable the Chord-section is filled with
       'not found' at the corresponding song."""
    results = []
    with open(input_path, newline='', encoding='utf-8') as csvfile:
        # Store the csv as a list with dictionaries inside.
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        # Go though all respective rows and process them if they have an url.
        for song in songs:
            song_name = song['Title']
            artist_name = song['Artist']
            tab_url = song['UG_link']

            chords = get_chords(tab_url)
            # Print to stdout and store in the result, that will be stored later.
            print(f'"""{song_name}""",{artist_name},{chords}')
            results.append({
                'Title': song_name,
                'Artist': artist_name,
                'Chords': chords if chords else 'not found'
            })

            # Add random delay or whatever so that we don't get blacklisted...
            # THIS IS VERY IMPORTANT!
            if chords:
                sleep(randint(1, 10))

    # Write result into new csv.
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Artist', 'Chords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f'results saved for {output_path}')
    return


def process_csv_to_harmonies(input_path: str, output_path: str) -> None:
    """Takes in a path to a csv in Title|Artist|Chords-format and writes to
       the output path a csv in format Title|Artist|Harmonies. If there are no
       chords for a song the Harmony-section is filled with 'not found'
    """
    results = []
    with open(input_path, newline='', encoding='utf-8') as csvfile:
        # ...
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        for song in songs:
            song_name = song['Title']
            artist_name = song['Artist']
            # Because I messed up earlier we also have to check for ''.
            # This is deprecated, since the issue was fixed, I will remove it later.
            if song['Chords'] == '' or song['Chords'] == 'not found':
                chords = None
            else:
                chords = eval(song['Chords'])

            # If chords is not None, then we can use them,
            # else we set harmony to the mentioned string.
            harmony = convert_song_to_harmony(
                chords) if chords else 'not found'

            print(f'"""{song_name}""",{artist_name},{harmony}')
            results.append({
                'Title': song_name,
                'Artist': artist_name,
                'Harmony': harmony
            })

    # ...
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Artist', 'Harmony']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f'results saved for {output_path}')
    return


def extract_csv_main_harmony(input_path: str, output_path: str) -> None:
    """Takes in a path to a csv in Title|Artist|Harmonies-format and writes to
       the output path a csv in format Title|Artist|Main Harmony. If there are no
       harmony for a song the Main Harmony-section is filled with 'not found'
    """
    results = []
    with open(input_path, newline='', encoding='utf-8') as csvfile:
        # ...
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        for song in songs:
            song_name = song['Title']
            artist_name = song['Artist']
            if song['Harmony'] == 'not found':
                harmony = None
            else:
                harmony = eval(song['Harmony'])

            # If chords is not None, then we can use them,
            # else we set harmony to the mentioned string.
            m_harmony = identify_main_harmony_2(harmony) if harmony else 'not found'

            print(f'"""{song_name}""",{artist_name},{m_harmony}')
            results.append({
                'Title': song_name,
                'Artist': artist_name,
                'Main_Harmony': m_harmony
            })

    # ...
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Artist', 'Main_Harmony']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f'results saved for {output_path}')
    return


# Set the path to the data-dir. Dependant on where Python is executed!
def convert_all_url_tables(super_path: str = '../../data') -> None:
    """This method is a cumulative run of 'process_csv_to_chords'
       with respect to the dataset we are using."""
    # Go through all years from 2005 to 2024 and process the correct csv-files.
    # After that store the chords in another table.
    for i in range(5, 25):
        input_path = f'{super_path}/chords/billboard_20{i:02d}.csv'
        output_path = f'{super_path}/chords_extracted/billboard_20{i:02d}.csv'
        process_csv_to_chords(input_path, output_path)


def convert_all_chord_tables(super_path: str = '../../data') -> None:
    """This method is a cumulative run of 'process_csv_to_harmonies'
       with respect to the dataset we are using."""
    # ...
    # ...
    for i in range(5, 25):
        input_path = f'{super_path}/chords_extracted/billboard_20{i:02d}.csv'
        output_path = f'{super_path}/chords_harmonies/billboard_20{i:02d}.csv'
        process_csv_to_harmonies(input_path, output_path)


def convert_all_harmony_tables(super_path: str = '../../data') -> None:
    """This method is a cumulative run of 'extract_csv_main_harmony'
       with respect to the dataset we are using."""
    # ...
    # ...
    for i in range(5, 25):
        input_path = f'{super_path}/chords_harmonies/billboard_20{i:02d}.csv'
        output_path = f'{super_path}/chords_main_harmonies/billboard_20{i:02d}.csv'
        extract_csv_main_harmony(input_path, output_path)


# Note: The following program was tested on the billboard of 2018,
# it should work on the others too, but they should be corrected, before running this!
#convert_all_url_tables()
#convert_all_chord_tables()
convert_all_harmony_tables()

