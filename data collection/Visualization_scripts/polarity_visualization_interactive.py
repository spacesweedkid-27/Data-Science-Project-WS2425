import pandas as pd
import glob
from textblob import TextBlob
import plotly.express as px
import re
import os

# Define the folder path
folder_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\BillBoard_Lyrics_preprocessed"

# Get all CSV file paths
file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

dataframes = []

# Read and process CSV files
for file in file_paths:
    filename = os.path.basename(file)
    match = re.search(r'(\d{4})', filename)  
    if match:
        year = int(match.group(1))
    else:
        continue

    df = pd.read_csv(file)
    df['Year'] = year  
    dataframes.append(df)

# Combine all data
if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)
else:
    raise ValueError("No valid CSV files found.")

# Ensure consistent column names
all_data.columns = all_data.columns.str.strip()

# Standardize lyrics column name if different
possible_columns = ['lyrics', 'Lyrics', 'text', 'lyric']
for col in possible_columns:
    if col in all_data.columns:
        all_data['lyrics'] = all_data[col]
        break

# Function to calculate polarity per word rather than full lyrics
def get_word_polarity(lyrics):
    words = str(lyrics).split()  # Split into individual words
    if not words:
        return None
    polarity_scores = [TextBlob(word).sentiment.polarity for word in words]
    return sum(polarity_scores) / len(polarity_scores)  # Average polarity

# Apply word-level polarity analysis
all_data['Polarity'] = all_data['lyrics'].apply(get_word_polarity)

# Drop rows with missing polarity values
all_data = all_data.dropna(subset=['Polarity'])

# Convert polarity bins to strings to avoid dtype issues
all_data['Polarity_bin'] = all_data['Polarity'].round(2)  # Round to 2 decimals for smoother bins

# Count occurrences in each polarity bin per year
polarity_distribution = all_data.groupby(['Year', 'Polarity_bin'], observed=False).size().reset_index(name='Count')

# Convert 'Polarity_bin' to string to prevent multi-index issues
polarity_distribution['Polarity_bin'] = polarity_distribution['Polarity_bin'].astype(str)

# Normalize within each year
polarity_distribution['Normalized_Count'] = polarity_distribution.groupby('Year')['Count'].transform(lambda x: x / x.sum())

# Create interactive histogram
fig = px.histogram(
    polarity_distribution,
    x='Polarity_bin',
    y='Normalized_Count',  # Use normalized values
    animation_frame="Year",
    title="Polarity Distribution of Song Lyrics Over Time (Normalized)",
    labels={"Polarity_bin": "Sentiment Polarity", "Normalized_Count": "Proportion of Songs"},
    template="plotly_dark"
)

# Update layout for better scaling
fig.update_layout(
    xaxis_title="Sentiment Polarity (-1 = Negative, 0 = Neutral, 1 = Positive)",
    yaxis_title="Proportion of Songs",
    xaxis=dict(range=[-1, 1]),  # Fix polarity range
    yaxis=dict(range=[0, 1]),  # Normalize scale
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True}]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
            ]
        )
    ]
)

# Show plot
fig.show()
