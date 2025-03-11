import os
import re
import pandas as pd

'''contains functions a couple of functions to prepare the data:
    - rename(path) renames all csv files into billboard_<year>.csv
    - fill_artists(path) copies the artists name from the previous entry into an empty cell'''

'''The specified path depends on where your source is. In my case, the venv is
located at "Data-Science-Project-WS2425", i.e. the root of the git repo. Might vary
in your case.'''
# TODO path as input on call

path = "data collection/scripts" # not the final path, but I don't wanna mess with the "real" data at this point

def rename_files(path):
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

def fill_artists(path):
    # idea: fill empty cells with NaN first
    # the use ffill or something
    for filename in os.listdir(path):
        if filename.endswith(".csv"):
            file = os.path.join(path, filename)

            # load csv into dataframe
            df = pd.read_csv(file)
            
            # rename Artist(s) to Artist because pandas has a problem with ( and )
            # column names apparently
            df.rename(columns={'Artist(s)': 'Artist'}, inplace=True)

            # remove leading spaces in case pandas is being weird
            df.columns.str.strip()

            # forward fill method because the empty cells always need to be populated
            # with the artist from the previous fill
            df['Artist'] = df['Artist'].ffill()

            # save changes to csv
            df.to_csv(file, index=False)
            print(f'updated {filename}')

#rename_files(path)
fill_artists(path)