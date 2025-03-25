#!/usr/bin/env python

import csv


def read_csv_into_dictlist(path: str, current: list[dict], year) -> None:
    with open(path, newline='', encoding='utf-8') as csvfile:
        # Store the csv as a list with dictionaries inside.
        reader = csv.DictReader(csvfile)
        songs = list(reader)
        
        columns_csv = list(songs[0].keys())
        #columns_cur = list(current[0].keys()) if current != [] else []

        has_year = 'Year' in columns_csv

        for i in range(len(songs)):
            # Store everything in one csv!
            adji = 100 * (year - 2005) + i
            if not has_year:
                    current[adji]['Year'] = year
                    current[adji]['Rank'] = i + 1
            for col in columns_csv:
                current[adji][col] = songs[i][col]
        return


super_path = '../../data'
table = [{} for _ in range(100) for _ in range(5, 25)]

for i in range(5, 25):
    # First pass: Title, Artist, Year, Rank, UG_Link, Chords
    input_path = f'{super_path}/chords/billboard_20{i:02d}.csv'
    read_csv_into_dictlist(input_path, table, 2000 + i)

    input_path = f'{super_path}/chords_extracted/billboard_20{i:02d}.csv'
    read_csv_into_dictlist(input_path, table, 2000 + i)

    input_path = f'{super_path}/chords_harmonies/billboard_20{i:02d}.csv'
    read_csv_into_dictlist(input_path, table, 2000 + i)

    input_path = f'{super_path}/chords_main_harmonies/billboard_20{i:02d}.csv'
    read_csv_into_dictlist(input_path, table, 2000 + i)

# Write result into new csv.
with open(f'{super_path}/merged.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=list(table[0].keys()))
    writer.writeheader()
    writer.writerows(table)
