import pandas as pd
import glob
import os
import re
from textblob import TextBlob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import random

# Define the folder path
folder_path = r"/Users/kapviq/Library/Mobile Documents/com~apple~CloudDocs/studies /CAU/sem5/DataScienceProject/Data-Science-Project-WS2425/data/Billboard_lyrics/Billboard_Lyrics_preprocessed"

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

    # Skip files without 'Lyrics' column
    if "Lyrics" not in df.columns:
        print(f"Skipping {filename}: 'Lyrics' column is missing")
        continue

    df['Year'] = year  # Add year column
    df['Polarity'] = df['Lyrics'].apply(get_polarity)  # Calculate polarity for each song's lyrics
    dataframes.append(df)

# Combine all data into a single dataframe
if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)
else:
    raise ValueError("No valid CSV files found.")

def update_fig_template(n_clicks):
    isDarkMode = n_clicks % 2 == 1  
    template = "plotly_dark" if isDarkMode else "morph"

    fig = make_subplots(rows=1, cols=1, subplot_titles=[""])

    if all_data.empty:
        print("No data available for visualization.")
        return None  

    for year in range(2005, 2025):
        year_data = all_data[all_data['Year'] == year]

        if not year_data.empty:
            avg_polarity = year_data['Polarity'].mean()
            color = "rgba(0, 102, 204, 0.8)"  

            fig.add_trace(go.Bar(
                x=[year], 
                y=[avg_polarity], 
                name=f'Year {year}', 
                marker=dict(color=color, opacity=0.7)
            ))

            fig.add_trace(go.Scatter(
                x=[year], 
                y=[avg_polarity], 
                mode='lines+markers', 
                marker=dict(size=8, color=color, opacity=0.7), 
                line=dict(color=color, width=2)
            ))

    fig.update_layout(
    width=4000,  # Increase width for higher resolution
    height=2200,  # Increase height for higher resolution
    
    xaxis_title="Year",
    yaxis_title="Average Polarity",
    showlegend=False,  
    hovermode="closest",
    template=template,
    paper_bgcolor='white',
    plot_bgcolor='white',
    xaxis=dict(
        type="category",  # Ensure labels are treated as categories
        tickmode="array", 
        tickvals=[str(year) for year in range(2005, 2025)],  # Explicitly set all years
        ticktext=[str(year) for year in range(2005, 2025)],  
        tickfont=dict(color='black'),  
        title_font=dict(color='black', size=14),
        tickangle=-90  # Rotates x-axis labels 90 degrees
    ),
    yaxis=dict(
        tickfont=dict(color='black'),  
        title_font=dict(color='black', size=14)  
    ),
    title_font=dict(color='black', size=16),  
    bargap=0.1  # Reduces space between bars

    )
    # high res export
    #fig.write_image(
    #   file = f'/Users/kapviq/Library/Mobile Documents/com~apple~CloudDocs/studies /CAU/sem5/DataScienceProject/Data-Science-Project-WS2425/{random.randint(0,1000)}.png',
    #    width = 1224,
    #    height = 650,
    #    scale = 4
    #)

    

    return fig  

# Example usage
n_clicks = 1
fig = update_fig_template(n_clicks)

if fig:
    fig.show()  
else:
    print("Figure generation failed.")

