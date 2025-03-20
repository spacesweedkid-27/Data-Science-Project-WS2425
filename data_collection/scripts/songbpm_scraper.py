import csv
import random 
import requests
import re
import warnings
from bs4 import BeautifulSoup

artist = 'red-hot-chili-peppers'
song = 'readymade'

def get_song_tempo(artist, song):
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

    url = f'https://songbpm.com/@{artist}/{song}'

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")

    tempo = [i.text for i in soup.select("span.bg-red-100, span[style='display-style']")]

    print(tempo)

get_song_tempo(artist, song)