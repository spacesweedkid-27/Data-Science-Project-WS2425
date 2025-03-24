import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import os


dash.register_page(__name__)

theme = 'plotly_dark' #  Initial theme that needs to be passed to graphs on load

heading = dbc.Container('We got some information about tempo here')
main_content = dbc.Container('Some information about this project goes here. '
'This content answers questions about what data sources we used, how the data '
'was processed and what assumptions were made. Whilest this information not '
'being listed in the official requirements provided by CAU, it still holds a lot'
'of value from a scientific standpoint.')

###################################
# GRAPHS
###################################

###################################
# Duration
###################################

# Data loading and processing
directory = 'data/durations'
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
df_list = []

for file in csv_files:
    df = pd.read_csv(os.path.join(directory, file))
    year = int(file.split('_')[1])  
    df['Year'] = year
    df_list.append(df)

df_all_years_duration = pd.concat(df_list, ignore_index=True)

###################################
# GRAPH TEMPLATE pt.1
###################################

# Here goes everything needed to create the graph such as data imports, 
# functions and other logic not related to the actual output object.

# Naming conventions:
# functions related to generation of the figure:            create_xaxis_yaxis_figtype()
#                                                           update_xaxis_yaxis_figtype()
#                                                          (or whatever else applies)
# temporary objects / interim results:                      xaxis_yaxis_figtype_tempdescriptor
# initialization object:                                    init_xaxis_yaxis_figtype
# (with tempdescriptor meaning a combination of words best
# describing the result of the interim / temporary object)

# We always need a create_function that receives the theme
# as a parameter. This is necessary for theme-changes.
# You don't necessarily need to use the plotly grpahic object (go) package.
# Plotly express (px) is fine as well. Just be aware, that the wrapper should
# remain a go.Figure for consistency.
'''
def create_xaxis_yaxis_figtype(theme):
    xaxis_yaxis_figtype = go.Figure(data = go.Figuretype(
        x = ...,
        y = ...,
        z = ...,
        ...
    )
    
    xaxis_yaxis_figtype.update_layout(
        # axis titles and so on
        autosize = True,
        height = 600, #  Can be changed to different value when it makes sense
        template = theme,
    )
    return xaxis_yaxis_figtype)
'''

# We always need to initialize the object once on load by using
# the create function. 
'''
init_xaxis_yaxis_figtype = create_xaxis_yaxis_figtype(theme)
'''

###################################
# GRAPH TEMPLATE pt.1
###################################

# Helper function to remove outliers using IQR method
def remove_outliers_duration(df, column):
    df_copy = df.copy()
    Q1 = df_copy[column].quantile(0.25)
    Q3 = df_copy[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df_copy[(df_copy[column] >= lower_bound) & (df_copy[column] <= upper_bound)]

# Helper function to format duration
def format_duration_min(minutes):
    total_seconds = int(minutes * 60)  
    mm = total_seconds // 60  
    ss = total_seconds % 60   
    return f"{mm}:{ss:02d}"

# Function to create the bar chart for song duration
def create_duration_years_bar_with_outliers(show_outliers, theme):
    df_original = df_all_years_duration  

    if 'show' in show_outliers:
        df_to_use = df_original
        title = "Average Song Durations Over 20 Years (With Outliers)"
    else:
        df_to_use = remove_outliers_duration(df_original, "Duration_min")
        title = "Average Song Durations Over 20 Years (Without Outliers)"
    
    df_grouped_duration = df_to_use.groupby("Year", as_index=False)["Duration_min"].mean()
    df_grouped_duration['Duration_formatted'] = df_grouped_duration['Duration_min'].apply(format_duration_min)
    
    y_max = 5  
    y_ticks = list(range(0, y_max))  
    y_labels = [format_duration_min(y) for y in y_ticks]  
    
    fig = px.bar(df_grouped_duration, x="Year", y="Duration_min", title=title)
    
    fig.update_traces(
        hovertemplate='<b>Year:</b> %{x}<br>' +
                      '<b>Duration (mm:ss):</b> %{customdata}<br>' +
                      '<b>Duration (minutes):</b> %{y:.2f}<extra></extra>',
        customdata=df_grouped_duration['Duration_formatted']
    )
    
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df_grouped_duration["Year"],
            tickformat=".0f",
            rangeslider=dict(visible=True), 
            type="linear",
            fixedrange=True  
        ),
        yaxis=dict(
            title="Duration",
            tickvals=y_ticks,
            ticktext=y_labels,
            fixedrange=True,  
            range=[0, y_max]  
        ),
        template = theme
    )
    
    return fig

def create_duration_boxplot(theme):
    fig = px.box(df_all_years_duration, x="Year", y="Duration_min", title="Song Duration Distribution Per Year (With Outliers)")
    
    df_grouped_duration = df_all_years_duration.groupby("Year", as_index=False)["Duration_min"].mean()
    df_grouped_duration['Duration_formatted'] = df_grouped_duration['Duration_min'].apply(format_duration_min)
    
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df_grouped_duration["Year"],  
            tickformat=".0f",
            rangeslider=dict(visible=True), 
            type="linear",
            fixedrange=True  
        ),
        yaxis=dict(
            title="Duration"  
        ),
        height = 800,
        template = theme
    )
    return fig

# Initialize the duration plot
init_duration_years_bar = create_duration_years_bar_with_outliers(['show'], theme)
init_duration_boxplot = create_duration_boxplot(theme)

###################################
# Tempo 
###################################

# Load and process Tempo data
def load_tempo_data():
    directory = 'data/tempo'
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    df_list_tempo = []
    for file in csv_files:
        df = pd.read_csv(os.path.join(directory, file))
        year = int(file.split('_')[1])
        df['Year'] = year
        df_list_tempo.append(df)
    
    df_all_years_tempo = pd.concat(df_list_tempo, ignore_index=True)
    
    df_all_years_tempo["Tempo"] = (
        df_all_years_tempo["Tempo"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s*BPM", "", regex=True)
        .apply(pd.to_numeric, errors="coerce")
    )
    
    df_all_years_tempo = df_all_years_tempo.dropna(subset=["Tempo"])
    df_all_years_tempo["Tempo"] = df_all_years_tempo["Tempo"].astype(int)
    
    df_grouped_tempo = df_all_years_tempo.groupby("Year", as_index=False)["Tempo"].mean()
    # Sort by year
    df_all_years_tempo = df_all_years_tempo.sort_values(by="Year")
    return df_all_years_tempo, df_grouped_tempo

df_all_years_tempo, df_grouped_tempo = load_tempo_data()

# Function to create the Tempo plot
def create_tempo_plot_with_range(year_range, theme):
    # Filter data based on selected years
    df_filtered_tempo = df_all_years_tempo[
        (df_all_years_tempo['Year'] >= year_range[0]) & 
        (df_all_years_tempo['Year'] <= year_range[1])
    ]
    filtered_grouped_tempo = df_filtered_tempo.groupby("Year", as_index=False)["Tempo"].mean()
    
    fig = px.scatter(df_filtered_tempo, x="Year", y="Tempo",
                     title="Average Song Tempo (BPM) Over The Last 20 Years ",
                     labels={"Tempo": "Tempo (BPM)", "Year": "Year"})
    
    # Line for average tempo values
    fig.add_scatter(x=filtered_grouped_tempo["Year"], y=filtered_grouped_tempo["Tempo"], 
                    mode="lines", name="Average", line=dict(width=2))
    
    fig.update_layout(
        xaxis=dict(type='category'),
        yaxis=dict(title="Tempo (BPM)"),
        template = theme
    )
    
    return fig

# Initialize the tempo plot
init_tempo_plot = create_tempo_plot_with_range([2005, 2024], theme)

###################################
# HTML ELEMENTS
###################################

# Define your html elements such as dbc.Container or dbc.Sliders here.
# Any related callbacks need to be defined in app.py
# Name these elements precicesly and plug them into the layout below.

###################################
# GRAPH TEMPLATE pt.2
###################################

# Naming conventions:
# for the actual figure that will be put into the layout:   xaixs_yaxis_figtype
# corresponding id:                                         xaxis-yaxis-figtype
# variable that holds slider / filter options:              xaxis_yaxis_figtype_slider
# corresponding id:                                         xaxis-yaxis-figtype-slider

# The actual HTML element for the graphic will be created here:
'''
xaxis_yaxis_figtype = dbc.Container([
    html.H3('Title'),
    <name of slider / filter toggle python object if it exists>,
    dcc.Graph(
        id = 'xaxis-yaxis-figtype',
        figure = init_xaxis_yaxis_figtype
    ), class_name = 'mt-3'
])
'''

# Interactive sliders / toggles / filters are defined here.
# Find out, what might be useful, look up documentation on how to create it.
# Important is, that the id corresponds to the naming conventions and accurately
# names what type of toggle / switch / whatever is used. This way, when looking
# through the callbacks in app.py it is easy to recognize what elements belong
# to which figure. The identification of where errors come from is also easier
# this way.
'''
xaxis_yaxis_figtype_slider = dcc.Slider(
    id = 'xaxis-yaxis-figtype-slider'
    ...
    )
'''

###################################
# GRAPH TEMPLATE pt.2
###################################

# Define the toggle for the Duration bar chart
duration_years_bar_toggle = dcc.Checklist(
    id='duration-years-bar-toggle',
    options=[{'label': 'Outlier', 'value': 'show'}],
    value=['show'],
    inline=True
)

# Container for the duration bar chart
duration_years_bar = dbc.Container([
    html.H3('Average Song Duration Over the Years'),
    duration_years_bar_toggle,
    dcc.Graph(
        id='duration-years-bar',
        figure=init_duration_years_bar
    )
], class_name='mt-3')

# Comtaimer for boxplot
duration_boxplot = dbc.Container([
    html.H3('Song Duration Distribution'),
    dcc.Graph(id='duration-boxplot', figure=init_duration_boxplot)
], class_name='mt-3')


# Tempo RangeSlider for selecting years
tempo_year_range_slider = dcc.RangeSlider(
    min=2005,
    max=2024,
    step=1,
    value=[2005, 2024],
    marks={str(year): str(year) for year in sorted(df_all_years_tempo["Year"].unique())},
    id='tempo-year-range-slider'
)

# Container for the Tempo plot
tempo_plot = dbc.Container([
    html.H3('Average Tempo Over the Years'),
    dcc.Graph(
        id='tempo-plot',
        figure=init_tempo_plot
    )
], class_name='mt-3')

# MAIN LAYOUT
layout = html.Div([heading,
                   main_content,
                   duration_years_bar,
                   duration_boxplot,
                   tempo_plot,
                   tempo_year_range_slider])