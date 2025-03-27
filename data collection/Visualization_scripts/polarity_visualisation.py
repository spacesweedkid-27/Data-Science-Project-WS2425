import pandas as pd
import glob
import os
import re
from textblob import TextBlob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Define the folder path
folder_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\BillBoard_Lyrics_preprocessed"
file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

dataframes = []

# Function to calculate polarity of the lyrics
def get_polarity(text):
    # Ensure the input is a string, if not return a polarity of 0
    if isinstance(text, str):
        return TextBlob(text).sentiment.polarity
    else:
        return 0.0  

# Read and process CSV files
for file in file_paths:
    filename = os.path.basename(file)
    match = re.search(r'(\d{4})', filename)  # Extract year from filename
    if match:
        year = int(match.group(1))
    else:
        continue

    
    df = pd.read_csv(file)

    # Skip files that don't have a 'Lyrics' column
    if "Lyrics" not in df.columns:
        print(f"Skipping {filename}: 'Lyrics' column is missing")
        continue

    df['Year'] = year  # Add year column
    df['Polarity'] = df['Lyrics'].apply(get_polarity)  # Calculate polarity for each song's lyrics
    dataframes.append(df)


if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)
else:
    raise ValueError("No valid CSV files found.")

# Below function has been modified with the help of Chatgpt
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

    title="Average Song Polarity over the Years",
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
        tickvals=[str(year) for year in range(2005, 2025)],  
        ticktext=[str(year) for year in range(2005, 2025)],  
        tickfont=dict(color='black'),  
        title_font=dict(color='black', size=14),
        tickangle=-90  # Rotates x-axis labels 90 degrees so everything fits
    ),
    yaxis=dict(
        tickfont=dict(color='black'),  
        title_font=dict(color='black', size=14)  
    ),
    title_font=dict(color='black', size=16),  
    bargap=0.1  
    )

    return fig  

# Example usage
n_clicks = 1
fig = update_fig_template(n_clicks)

if fig:
    # Export the figure with small base resolution but high scale for printing
    pio.write_image(fig, "output.png", width=900, height=500, scale=2)
    fig.show()

else:
    print("Figure generation failed.")
    