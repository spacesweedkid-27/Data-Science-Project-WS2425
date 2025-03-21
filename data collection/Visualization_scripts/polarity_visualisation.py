import os
import glob
import pandas as pd
import re
import plotly.graph_objects as go
from textblob import TextBlob
import numpy as np

# 📌 1️⃣ Daten laden und zusammenführen
folder_path = r"C:\Users\MikaM\OneDrive\Dokumente\Uni-Cau-kiel\Data-Science-Project\Data-Science-Project-WS2425\data\Billboard_lyrics\BillBoard_Lyrics_preprocessed"

file_paths = glob.glob(os.path.join(folder_path, "*.csv"))
dataframes = []

for file in file_paths:
    filename = os.path.basename(file)
    match = re.search(r'(\d{4})', filename)  # Jahr aus Dateinamen extrahieren
    if match:
        year = int(match.group(1))
    else:
        continue

    df = pd.read_csv(file)
    df['Year'] = year
    dataframes.append(df)

if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)
else:
    raise ValueError("Keine gültigen CSV-Dateien gefunden.")

# 📌 2️⃣ Funktion zur Berechnung der Wortpolarität
def get_word_polarity(text):
    if isinstance(text, str):  
        words = text.split()
        polarities = [TextBlob(word).sentiment.polarity for word in words]
        return polarities
    return []

all_data['Polarity'] = all_data['Lyrics'].apply(get_word_polarity)

# 📌 3️⃣ Daten für die Visualisierung vorbereiten
years = list(range(2005, 2025))
polarities_by_year = {year: [] for year in years}
mean_polarities = {}

for year in years:
    yearly_data = all_data[all_data['Year'] == year]
    if not yearly_data.empty:
        all_polarities = [p for sublist in yearly_data['Polarity'] for p in sublist]
        polarities_by_year[year] = all_polarities
        mean_polarities[year] = np.mean(all_polarities) if all_polarities else 0  # Durchschnitt berechnen
    else:
        mean_polarities[year] = 0

# 📌 4️⃣ Interaktive Visualisierung mit Optimierung
fig = go.Figure()

for year in years:
    polarities = np.array(polarities_by_year[year])
    
    # Trennen der neutralen Werte (Polarität = 0)
    negative = polarities[polarities < 0]
    neutral = polarities[polarities == 0]
    positive = polarities[polarities > 0]

    # Histogramme für jede Polaritätsklasse
    fig.add_trace(go.Histogram(
        x=negative,
        name=f'Negativ ({year})',
        marker_color='red',
        opacity=0.7,
        visible=True if year == 2005 else False
    ))

    fig.add_trace(go.Histogram(
        x=positive,
        name=f'Positiv ({year})',
        marker_color='blue',
        opacity=0.7,
        visible=True if year == 2005 else False
    ))

    fig.add_trace(go.Histogram(
        x=neutral,
        name=f'Neutral ({year})',
        marker_color='gray',
        opacity=0.5,
        visible=True if year == 2005 else False
    ))

    # 🔥 Durchschnittliche Polarität als dünne vertikale Linie 🔥
    fig.add_trace(go.Scatter(
        x=[mean_polarities[year], mean_polarities[year]],  # Linie bei Durchschnittswert
        y=[1, 10**5],  # Höhe der Linie (angepasst für logarithmische Skalierung)
        mode="lines",
        line=dict(color="orange", width=2, dash="dash"),  # Farbe: Orange, Dünn, Gestrichelt
        name=f'Durchschnitt ({year})',
        visible=True if year == 2005 else False
    ))

# 📌 5️⃣ Korrekte Slider-Definition mit optimierter Sichtbarkeit
steps = []
for i, year in enumerate(years):
    step = dict(
        method="update",
        args=[{"visible": [j // 4 == i for j in range(len(years) * 4)]}],
        label=str(year)
    )
    steps.append(step)

fig.update_layout(
    title="Verteilung der Wortpolaritäten in Songtexten (2005–2024)",
    xaxis_title="Polarität",
    yaxis_title="Anzahl der Wörter",
    barmode='overlay',  # Histogramme überlagern sich leicht für bessere Sichtbarkeit
    yaxis_type="log",  # Logarithmische Skalierung
    sliders=[{
        "active": 0,  # Startjahr 2005
        "currentvalue": {
            "visible": True,
            "prefix": "Jahr: ",
            "font": {"size": 20}
        },
        "steps": steps
    }]
)

# 📌 6️⃣ Visualisierung anzeigen
fig.show()
