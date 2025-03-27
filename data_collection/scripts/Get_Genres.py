import requests
import pandas as pd
import time
import re  # For cleaning artist names
from tqdm import tqdm  # Progress bar
from dotenv import load_dotenv
import os

#Last.fm API i used
load_dotenv()
API_KEY =  "5e0cefeecb9bb463ea191ada4938a63f"

# Load CSV files
df = pd.read_csv(r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\raw\billboard_2013.csv")

# Only use first Artist without the features for Api handling
def clean_artist_name(artist):
    return re.split(r' feat\.| featuring | & |, ', artist, flags=re.IGNORECASE)[0].strip()

# Function to fetch tags from Last.fm
#Below function has been modified with the help of Chatgpt
def get_tags(artist, title, num_tags=3):
    artist = clean_artist_name(artist)  
    
    # Get Tags for the Songs
    url_track = f"http://ws.audioscrobbler.com/2.0/?method=track.gettoptags&artist={artist}&track={title}&api_key={API_KEY}&format=json"
    url_artist = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist={artist}&api_key={API_KEY}&format=json"

    try:
        response = requests.get(url_track, timeout=5).json()
        tags = response.get("toptags", {}).get("tag", [])

        if not tags:  # If no track tags, try fetching artist tags
            response = requests.get(url_artist, timeout=5).json()
            tags = response.get("toptags", {}).get("tag", [])

        if tags:
            top_tags = [tag["name"] for tag in tags[:num_tags]]  # Get top `num_tags` tags
            return ", ".join(top_tags)  # Return as comma-separated string
        else:
            return "Unknown"  
    except Exception as e:
        print(f"Error fetching tags for {title} by {artist}: {e}")
        return "Error"

# Apply function to each row with a progress bar
tqdm.pandas()
df["Top_Tags"] = df.progress_apply(lambda row: get_tags(row["Artist"], row["Title"]), axis=1)

# Save the updated CSV file
df.to_csv("billboard_2013_with_tags.csv", index=False)
