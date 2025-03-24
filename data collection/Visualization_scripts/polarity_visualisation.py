import pandas as pd
import glob
import os
import re
from textblob import TextBlob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Define the folder path
folder_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\BillBoard_Lyrics_preprocessed"

# Get all CSV file paths
file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

dataframes = []

# Function to calculate polarity of the lyrics
def get_polarity(text):
    # Ensure the input is a string, if not return a polarity of 0
    if isinstance(text, str):
        return TextBlob(text).sentiment.polarity
    else:
        return 0.0  # If the value is not a string, return neutral polarity (0)

# Read and process CSV files
for file in file_paths:
    filename = os.path.basename(file)
    match = re.search(r'(\d{4})', filename)  # Extract year from filename
    if match:
        year = int(match.group(1))
    else:
        continue

    # Read the CSV file
    df = pd.read_csv(file)
    df['Year'] = year  # Add year column
    df['Polarity'] = df['Lyrics'].apply(get_polarity)  # Calculate polarity for each song's lyrics
    dataframes.append(df)

# Combine all data into a single dataframe
if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)
else:
    raise ValueError("No valid CSV files found.")

# Create an interactive figure with Plotly
fig = make_subplots(rows=1, cols=1, subplot_titles=["Polarität der Songtexte über Jahre"])

# Add both bars and line for each year
for year in range(2005, 2025):  # From 2005 to 2024
    year_data = all_data[all_data['Year'] == year]
    
    # Calculate the average polarity for the year
    avg_polarity = year_data['Polarity'].mean()
    
    # Add bars for each year
    fig.add_trace(go.Bar(
        x=[year], 
        y=[avg_polarity], 
        name=f'Jahr {year}',
        marker=dict(color='rgba(255, 99, 132, 0.5)', opacity=0.7)
    ))
    
    # Add a line for each year
    fig.add_trace(go.Scatter(
        x=[year], 
        y=[avg_polarity], 
        mode='lines+markers',  # Line + Marker
        name=f'Jahr {year}',
        text=[f'{year}: {avg_polarity:.2f}'],
        textposition="top center",
        marker=dict(size=8, color='rgb(255, 99, 132)', opacity=0.7),
        line=dict(color='rgb(255, 99, 132)', width=2)  # Add line
    ))

# Layout for the visualization
fig.update_layout(
    title="Durchschnittliche Polarität der Songtexte über Jahre",
    xaxis_title="Jahr",
    yaxis_title="Durchschnittliche Polarität",
    showlegend=True,
    hovermode="closest",
    template="plotly_dark"
)

# Show the plot
import plotly.io as pio
pio.renderers.default = "browser"
fig.show()
