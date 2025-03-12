import csv
import random
import requests
import re
import warnings
import time
import json
import html


def search(song, artist):
    ''' Queries ultimate-guitar.com for chords for a (artist, song) combination.
    '''

    # Maybe this helps preventing ip-bans?
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36 Kinza/4.9.0',
            'Mozilla/5.0 (Linux; Android 11; RMX3191) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36 Kinza/4.9.0',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 (Chromium GOST) Safari/537.36',
            'Dalvik/2.1.0 (Linux; U; Android 8.1.0; vivo X9s Build/OPM1.171019.019)',
            'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-A710L Build/NRD90M)',
            'Mozilla/5.0 (Linux; Android 9; FIG-LX1 Build/HUAWEIFIG-L11; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.120 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.1.0; SM-J710GN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
            'Opera/9.80 (MAUI Runtime; Opera Mini/4.4.39001/174.101; U; id) Presto/2.12.423 Version/12.16',
            'Mozilla/5.0 (Linux; Android 10; AOYODKG_A38 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Safari/537.36'
        ])
    }

    # Formulate the query that will be injected into the URL.
    query = f'"{song}+{artist}'
    # We specify type=300 since it means that we want to search for chords.
    url = f'https://ultimate-guitar.com/search.php?search_type=title&value={query}&type=300'

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'failed to fetch search results for {song} by {artist}')
        # Remove "featuring artist2" from query and try again.
        cleaned_artist = remove_featuring(artist)
        print(f'cleaned artist {artist} to {cleaned_artist}')
        # Run again with cleaned artist.
        if cleaned_artist != artist:
            # This whole part is really not pretty to be honest, but I ran into
            # some issues with recursive calls, so I wanna avoid that. The
            # scraping process is slow enough as it is.
            # See below for detailed comments about what each of these lines
            # does.
            query = f'"{song}+{cleaned_artist}'
            url = f'https://ultimate-guitar.com/search.php?search_type=title&value={query}&type=300'

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f'failed to fetch search results during second try for {song} by {cleaned_artist}')
                return None
            chords_url = check_for_chords_type(response.text)

            if chords_url:
                if 'official' in chords_url:
                    warnings.warn(f'official found in link for {song} by {artist}')
                    return None
                # if lowercase_song(song) in chords_url:
                 #   return chords_url
                # return None
                return chords_url

            print(f'no chords found for {song} by {artist}')
            return None

        return None

    chords_url = check_for_chords_type(response.text)

    if chords_url:
        if 'official' in chords_url:
            warnings.warn(f'official found in link for {song} by {artist}')
            return None
        # if lowercase_song(song) in chords_url:
         #   return chords_url
        # return None
        return chords_url

    print(f'no chords found for {song} by {artist}')
    return None

    # Ultimate Guitar hides the links within JSON structures on load, so instead
    # of accessing them through their a href tag we'll need to look for the
    # appropriate link structure in the returned JSON. Currently this works
    # under the assumption that the first link found is always a "chords"-tab,
    # as this is the most common search-result, but especially for older songs
    # this might vary. A solution might be to also check whether "chords" is
    # somewhere within the link, as it usually is, but I can't be 100% sure
    # about this right now. The next steps in the processing-workflow will
    # reveal if I need to refine a couple of things.

    # match = re.search(r'https://tabs\.ultimate-guitar\.com/tab/[^"}]+',
    #                 response.text)
    # match = re.search(r'https://tabs\.ultimate-guitar\.com/tab/[^&]*',
    #               response.text)

    # if match:
    # print(match.group(0))  # debugging purposes
    # Working under the assumption that if a tab is not online because of
    # licensing, the official tab will be returned by UG, which usually
    # contain the word "official" within the url. Filtering for that and
    # raising a custom warning in the commandline, which might later be
    # logged in a log-file. Currently not returning "not found" to the file,
    # as I want to manually check occurrences for official tabs.
    '''if 'official' in match.group(0):
        warnings.warn(f'official found in link for {song} by {artist}')
        return None
    if lowercase_song(song) in match.group(0):
        return match.group(0)
    else:
        warnings.warn(f'Might be the wrong chords for {song} by {artist}')
        return match.group(0)'''

    # if no match is found, return None so cell remains empty and can be skipped
    # in further processing
    # return None


def remove_featuring(artist):
    ''' Removes 'featuring' and everything after that from the artist name, as
    this might cause no results to appear on ultimate-guitar.com.'''
    return re.split(r'\s+featuring\s+|\s+feat\.\.s+|\s+ft\.\s+', artist, flags=re.IGNORECASE)[0]


def lowercase_song(song):
    return song.replace(" ", "-").lower()


def check_for_chords_type_old(response_text):
    ''' Checks whether the url that was found contains the "chords"-type.'''
    decoded = html.unescape(response_text)

    match = re.search(r'(\[\{.*?\}\])', decoded, re.DOTALL)

    if not match:
        print('no json data in reponse')
        return None
    try:
        # convert data to python list for easier search
        # this is a shitton of chars
        json_data = json.loads(match.group(1)[:5000])

        tab_url = None  # initialize as None in case no chords are found

        json_data = json_data.replace("\\'", "'")
        json_data = json_data.replace("\\", "")

        for item in json_data:
            if item.get('type', '').lower() == 'chords':
                tab_url = item.get('tab_url')
                if 'pro/?app_utm_source' in tab_url:
                    continue
            return tab_url
    except json.JSONDecodeError as e:
        print(f'json decoding failed: {e}')
        print(f'json segment: {match.group(1)[:500]}')
    return None


def check_for_chords_type(response):
    '''Newer implementation to check if a URL contains chords.'''
    clean_response = html.unescape(response)
    # debugging:
    print(clean_response[:500])  # Print snippet

    matches = re.findall(r'https://tabs\.ultimate-guitar\.com/tab/[^"]*chords[^"]*', clean_response)
    for url in matches:
        print(url)
        if "pro/?app_utm_source" not in url:  # Skip official/pro versions.
            return url
    return None  # return None if nothing was found.


def get_ug_links(input, output):
    ''' Reads (song, artist) information from svg files, calls search() for
    every (song, artist) combination and saves the found link into a new
    svg. If there is no link to be found, the cell remains empty.'''

    # read chart csv, copy info to new csv and add link
    with open(input, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = list(reader)

        # results list to buffer title, artist and links
        results = []
        for song in songs:
            song_name = song['Title']
            artist_name = song['Artist']

            # print(f'Searching for {song_name} by {artist_name}')
            # currently it looks like UG doesn't ban automatic queries as
            # quickly, but I haven't found reliable information about that yet
            # and have only tested with a small amount of queries (5-7 per test
            # run), which might also be the reason I haven't been banned yet.
            # A sleep timer might be a solution but for testing it just took
            # too long.

            # randomly sleep between queries to not get locked out
            time.sleep(random.randint(1, 10))
            tab_url = search(song_name, artist_name)

            results.append({
                'Title': song_name,
                'Artist': artist_name,
                'UG_link': tab_url if tab_url else 'not found'
            })

        # write result into new csv
        with open(output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Artist', 'UG_link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f'results saved for {output}')


# it might be useful to add automation to this process as well
# get_ug_links('data collection/scripts/billboard_2024.csv',
 #          'data collection/scripts/billboard_2024_chords.csv')
# print(search("Girls Like You", "Maroon 5 featuring Cardi B"))
# print(search("Thank you, next", "Ariana Grande"))
