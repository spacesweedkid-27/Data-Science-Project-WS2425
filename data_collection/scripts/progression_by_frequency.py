#!/usr/bin/env python


import csv


def convert_all_harmony_tables(super_path: str = '../../data') -> None:
    """Lists all main harmonies/intervals and their frequency in the dataset."""
    # We set (,) as "not found".
    current_h = {tuple() : 0}
    current_i = {tuple() : 0}
    for i in range(5, 25):
        input_path = f'{super_path}/chords_main_harmonies/billboard_20{i:02d}.csv'
        # Process the year f'20{i:02d}'.
        # 'current_h' and 'current_i' are iterative variables.
        current_h, current_i = get_all_main_harmonies_and_intervals(input_path, current_h, current_i)

    # Sort all harmonies by their frequency.
    keys_h = list(current_h.keys())
    list.sort(keys_h, key=lambda x : -current_h[x])
    # Sort all ...
    keys_i = list(current_i.keys())
    list.sort(keys_i, key=lambda x : -current_i[x])
    
    print("Main Harmony:\tFrequency")
    # Print out all harmonies and their frequency.
    for entry_h in keys_h:
        print(f"{entry_h}:\t{current_h[entry_h]}")
    
    print()
    print("Main Interval Harmony:\tFrequency")
    # ...
    for entry_i in keys_i:
        print(f"{entry_i}:\t{current_i[entry_i]}")


def get_all_main_harmonies_and_intervals(input_path: str, current_h: dict[tuple[int, ...], int], current_i: dict[tuple[int, ...], int]) -> tuple[dict[tuple[int, ...], int], dict[tuple[int, ...], int]]:
    """Processes a Main_Harmony-csv by counting all harmonies
       and intervals and pushing them into the current result.
    """
    results_h = current_h
    results_i = current_i

    with open(input_path, newline='', encoding='utf-8') as csvfile:
        # ...
        reader = csv.DictReader(csvfile)
        songs = list(reader)
        
        # Process all songs and increase the counter for
        # the correlating Main_Harmony.
        for song in songs:
            if song['Main_Harmony'] != 'not found':
                m_harmony = (song['Main_Harmony'])
                if m_harmony not in results_h.keys():
                    results_h[m_harmony] = 1
                else:
                    results_h[m_harmony] += 1
            else:
                results_h[tuple()] += 1

        # Process all songs and increase the counter for
        # the correlating ...
        for song in songs:
            if song['Main_Interval_Harmony'] != 'not found':
                m_interval = (song['Main_Interval_Harmony'])
                if m_interval not in results_i.keys():
                    results_i[m_interval] = 1
                else:
                    results_i[m_interval] += 1
            else:
                results_i[tuple()] += 1
    return results_h, results_i

if __name__ == 'main':
    convert_all_harmony_tables()
