#!/usr/bin/env python


import csv


def convert_all_harmony_tables(super_path: str = '../../data') -> None:
    """Lists all main harmonies and their frequency in the dataset."""
    # We set (,) as "not found".
    current = {tuple() : 0}
    for i in range(5, 25):
        input_path = f'{super_path}/chords_main_harmonies/billboard_20{i:02d}.csv'
        # Process the year 20{i:02d}.
        # 'current' is a temporary variable that evolves.
        current = get_all_main_harmonies(input_path, current)
    # Sort all harmonies by their frequency.
    keys = list(current.keys())
    list.sort(keys, key=lambda x : -current[x])
    # Print out all harmonies and their frequency.
    for entry in keys:
        print(f"{entry} : {current[entry]}")


def get_all_main_harmonies(input_path: str, current: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    """Processes a Main_Harmony-csv by counting all harmonies
       and pushing them into the current result.
    """
    results = current
    with open(input_path, newline='', encoding='utf-8') as csvfile:
        # ...
        reader = csv.DictReader(csvfile)
        songs = list(reader)
        
        # Process all songs and increase the counter for
        # the correlating Main_Harmony.
        for song in songs:
            if song['Main_Harmony'] != 'not found':
                m_harmony = eval(song['Main_Harmony'])
                if m_harmony not in results.keys():
                    results[m_harmony] = 1
                else:
                    results[m_harmony] += 1
            else:
                results[tuple()] += 1
    return results


def __main__():
    convert_all_harmony_tables()
