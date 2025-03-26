import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import glob
import os
import re
from collections import Counter
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO

nltk.download('punkt')

STOP_WORDS = {"wan", "na", "ta", "ca"}  

folder_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\BillBoard_Lyrics_preprocessed"
file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

dataframes = []
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

all_data = pd.concat(dataframes, ignore_index=True)
all_lyrics = ' '.join(all_data['Lyrics'].dropna()).lower()  

# Funktion zum Erstellen der Word Cloud
def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=STOP_WORDS).generate(text)
    
    img = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return "data:image/png;base64," + base64.b64encode(img.read()).decode()

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Billboard Lyrics Word Cloud"),
    html.Img(id='wordcloud-image')
])

# Callback für Word Cloud
@app.callback(
    Output('wordcloud-image', 'src'),
    Input('wordcloud-image', 'id')
)
def update_wordcloud(_):
    return generate_wordcloud(all_lyrics)

if __name__ == '__main__':
    app.run(debug=True)
