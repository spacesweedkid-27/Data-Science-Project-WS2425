import pandas as pd
from dash import Dash, dash_table, dcc, html, clientside_callback, callback
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import os


dash.register_page(__name__)

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

df_all_years = pd.concat(df_list, ignore_index=True)

####################################
# Helper functions
####################################
# Helper function to remove outliers using IQR method
def remove_outliers(df, column):
    df_copy = df.copy()
    Q1 = df_copy[column].quantile(0.25)
    Q3 = df_copy[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df_copy[(df_copy[column] >= lower_bound) & (df_copy[column] <= upper_bound)]

# Helper function to format duration
def format_duration(minutes):
    total_seconds = int(minutes * 60)  
    mm = total_seconds // 60  
    ss = total_seconds % 60   
    return f"{mm}:{ss:02d}"



# Naming conventions:
# functions related to generation of the figure:            create_xaxis_yaxis_figtype()
#                                                           update_xaxis_yaxis_figtype()
#                                                           (or whatever else applies)
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


# Function to create the bar chart
def create_duration_years_bar(show_outliers):
    df_original = df_all_years  

    if 'show' in show_outliers:
        df_to_use = df_original
        title = "Average Song Durations Over 20 Years (With Outliers)"
    else:
        df_to_use = remove_outliers(df_original, "Duration_min")
        title = "Average Song Durations Over 20 Years (Without Outliers)"
    
    df_grouped = df_to_use.groupby("Year", as_index=False)["Duration_min"].mean()
    df_grouped['Duration_formatted'] = df_grouped['Duration_min'].apply(format_duration)
    
    y_max = 5  
    y_ticks = list(range(0, y_max))  
    y_labels = [format_duration(y) for y in y_ticks]  
    
    fig = px.bar(df_grouped, x="Year", y="Duration_min", title=title)
    
    fig.update_traces(
        hovertemplate='<b>Year:</b> %{x}<br>' +
                      '<b>Duration (mm:ss):</b> %{customdata}<br>' +
                      '<b>Duration (minutes):</b> %{y:.2f}<extra></extra>',
        customdata=df_grouped['Duration_formatted']
    )
    
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df_grouped["Year"],
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
        )
    )
    
    return fig

# We always need to initialize the object once on load by using
# the create function. 
'''
init_xaxis_yaxis_figtype = create_xaxis_yaxis_figtype(theme)
'''
init_duration_years_bar = create_duration_years_bar(['show'])


###################################
# HTML ELEMENTS
###################################

# Define your html elements such as dbc.Container or dbc.Sliders here.
# Any related callbacks need to be defined in app.py
# Name these elements precisely and plug them into the layout below.

duration_years_bar_toggle = dcc.Checklist(
    id='duration-years-bar-toggle',
    options=[{'label': 'Outlier', 'value': 'show'}],
    value=['show'],
    inline=True
)

duration_years_bar = dbc.Container([
    html.H3('Average Song Duration Over the Years'),
    duration_years_bar_toggle,
    dcc.Graph(
        id='duration-years-bar',
        figure=init_duration_years_bar
    )
], class_name='mt-3')

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
], class_name='mb-5')
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
# MAIN LAYOUT
###################################

# Layout elements can be plugged in here.
# Don't change the name from layout to anything else. Dash page
# registry needs this attribute to properly load the content.
layout = html.Div([heading,
                   main_content,
                   
                   duration_years_bar])
                   # More html / dbc Elements can be added here
                   # in the preferred order. Don't forget the commas.