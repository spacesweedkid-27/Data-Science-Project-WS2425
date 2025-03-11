import os
import re

'''contains functions a couple of functions to prepare the data:
    - rename(path) renames all csv files into billboard_<year>.csv
    - fill_artists(path) copies the artists name from the previous entry into an empty cell'''

'''The specified path depends on where your source is. In my case, the venv is
located at "Data-Science-Project-WS2425", i.e. the root of the git repo. Might vary
in your case.'''
# TODO path as input on call

path = "data collection/scripts" # not the final path, but I don't wanna mess with the "real" data at this point

def rename(path):
    # function looks for and renames csv files
    for filename in os.listdir(path):
        '''safety-reasons: the raw data folder should only contain csv-files, but in
        case macos does wild bin files again, ignore them'''
        if filename.endswith(".csv"):
            # looks for the last 4 digits of the filename of any csv files (should contain the year)
            match = re.search(r'(\d{4})\.csv$', filename)
            #print(f'found match {match}') # debugging
            if match:
                # match.group(1) contains year
                year = match.group(1)
                new_name = f'billboard_{year}.csv'

                old_path = os.path.join(path, filename)
                new_path = os.path.join(path, new_name)

                os.rename(old_path, new_path)
                print(f'renamed: {filename} to {new_name}')
    return None

# TODO fill empty cells with artist from previous entry
#def fill_artists(path):
    # fill empty cells with NaN first
    # the use ffill or something