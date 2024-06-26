import plotly.express as px
import plotly.io as pio
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from website.song_characteristics import *

# Function to create a scatterplot for general statistics 
def make_general_scatter(user_id):
    conn, cursor = db_connect("spotify_db3.db")
    cursor.execute("SELECT a.*, b.Song_name FROM Streaming_data a JOIN Songs b ON a.Song_ID = b.Song_ID WHERE User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()

    dataframe = pd.DataFrame(data, columns = ["User_ID", "Song_ID", "Artist_ID", "end_time", "ms_played", "song_name"])   
    dataframe["ms_played"] = dataframe["ms_played"].astype(int)
    dataframe["sec_played"] = dataframe["ms_played"]/1000
    dataframe = dataframe.drop(["ms_played"], axis=1)
    dataframe = dataframe.groupby("song_name")["song_name"].size().reset_index(name="count")
    dataframe = dataframe.groupby('count').size().reset_index(name='number_of_songs')
    plot_df = dataframe.copy()
    
    fig = px.scatter(x=plot_df["number_of_songs"], y=plot_df["count"], labels={"x":"Number of songs", "y":"Number of plays"}, color_discrete_sequence=['#1DB954'])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font_color="white",
        title = {
            "text":"Do you attach to songs?",
            "x": 0.5,
            "xanchor":"center",
            "yanchor": "top"
        },
        width=1200,
        height=600
    )
    fig.update_xaxes(color="white")
    fig.update_yaxes(color="white")
    return fig

# Function to generate heatmap for general statistics (plot below scatterplot)
def make_general_heatmap(user_id):
    color_stops = [[0, 'rgb(0,0,0)'], [0.25, 'rgb(0,68,27)'], [0.5, 'rgb(0,109,44)'], [0.75, 'rgb(255,255,191)'], [1, 'rgb(253,174,97)']]
    conn, cursor = db_connect("spotify_db3.db")
    cursor.execute("SELECT a.*, b.Song_name FROM Streaming_data a JOIN Songs b ON a.Song_ID = b.Song_ID WHERE User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()

    dataframe = pd.DataFrame(data, columns = ["User_ID", "Song_ID", "Artist_ID", "end_time", "ms_played", "song_name"])  

    # Convert date
    dataframe['date'] = pd.to_datetime(dataframe['end_time'])
    dataframe['date'] = pd.to_datetime(dataframe['date'].dt.date)
    # Extract the hour and week from the datetime
    dataframe['hour'] = pd.to_datetime(dataframe['end_time']).dt.hour
    dataframe['week'] = pd.to_datetime(dataframe['end_time']).dt.isocalendar().week
    # Group the data by week and hour
    df_grouped = dataframe.groupby(['week', 'hour']).size().reset_index(name='count')
    # Add missing hours and weeks
    weeks = range(1, 53)
    hours = range(0, 24)
    new_index = pd.MultiIndex.from_product([weeks, hours], names=['week', 'hour'])
    df_plot = df_grouped.set_index(['week','hour']).reindex(new_index, fill_value=0).reset_index()
    
    # Set minimal/maximum values on yaxis and prepare the plot
    y_min = df_plot[df_plot["count"] != 0]["week"].min()
    y_max = df_plot[df_plot["count"] != 0]["week"].max()

    fig = go.Figure(data=go.Heatmap(
                       x=df_plot['hour'],
                       y=df_plot['week'],
                       z=df_plot['count'],
                       type='heatmap',
                       colorscale=color_stops,
                       zmin=-1,
                       zmax=df_plot["count"].max(),
                       colorbar=dict(tickcolor="white", tickfont=dict(color="white")),
                       hovertemplate="Hour: %{x} <br>Week: %{y}<br>Number of plays: %{z}<extra></extra>"

    ))
    fig.update_layout(xaxis_title="Hour of the day", 
                      yaxis_title="Week of the year", 
                      yaxis_range=(y_min, y_max),
                      xaxis_tick0=0,
                      xaxis_dtick=3,
                      yaxis_dtick=3,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      title_font_color="white",
                      title = {
                                "text":"When have you listened to music?",
                                "x": 0.5,
                                "xanchor":"center",
                                "yanchor": "top"}, 
                      showlegend=False,
                      width=1200,
                      height=600
    )
    fig.update_xaxes(color="white")
    fig.update_yaxes(color="white")

    return fig

# Function to create first plot for detailed statistics (songs characteristics throughout the year)
def song_statistics_through_the_year(user_id):

    conn, cursor = db_connect("spotify_db3.db")
    cursor.execute("SELECT a.end_Time, b.* FROM Streaming_data a JOIN Songs_features b ON a.Song_ID = b.Song_ID WHERE User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()
    dataframe = pd.DataFrame(data, columns=["end_time", "song_id", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
    dataframe = normalize(dataframe, ["tempo", "loudness"])
    dataframe["month"] = pd.to_datetime(dataframe["end_time"]).dt.month
    
    plot_data = dataframe.drop(["end_time", "song_id"], axis=1).groupby("month").agg("mean").reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=plot_data['danceability'], x=plot_data['month'],
                        mode='lines',
                        name='danceability'))
    fig.add_trace(go.Scatter(y=plot_data['energy'], x=plot_data['month'],
                             mode='lines',
                             name='energy'))
    fig.add_trace(go.Scatter(y=plot_data['tempo'], x=plot_data['month'],
                             mode='lines',
                             name='tempo'))
    fig.add_trace(go.Scatter(y=plot_data['acousticness'], x=plot_data['month'],
                             mode='lines',
                             name='acousticnesss'))
    fig.add_trace(go.Scatter(y=plot_data['instrumentalness'], x=plot_data['month'],
                             mode='lines',
                             name='instrumentalness'))
    fig.add_trace(go.Scatter(y=plot_data['loudness'], x=plot_data['month'],
                             mode='lines',
                             name='loudness'))

    fig.update_layout(xaxis_title="Month of the year", 
                      yaxis_title="Mean of the statistic", 
                      yaxis_range=(0, 1),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      title_font_color="white",
                      legend_font_color="white",
                      title = {
                                "text":"What are the specifics of the songs you listen to?",
                                "x": 0.5,
                                "xanchor":"center",
                                "yanchor": "top",
                                "font_size": 22}, 
                      width=1400,
                      height=600
    )
    fig.update_xaxes(color="white")
    fig.update_yaxes(color="white")
    return fig

# Function to create a radar plot for detailed statistics
def make_radar(user_id):
    conn, cursor = db_connect("spotify_db3.db")
    cursor.execute("SELECT a.end_Time, b.* FROM Streaming_data a JOIN Songs_features b ON a.Song_ID = b.Song_ID WHERE User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()
    dataframe = pd.DataFrame(data, columns=["end_time", "song_id", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
    dataframe = normalize(dataframe, ["tempo", "loudness"])
    dataframe = dataframe.drop(["end_time", "song_id"], axis=1).agg("mean")

    fig = go.Figure(go.Scatterpolar(
        name = "Your songs with highest:",
        r = [dataframe["danceability"], dataframe["energy"], dataframe["acousticness"], dataframe["instrumentalness"], dataframe["loudness"], dataframe["tempo"]],
        theta = ["danceability", "energy", "accousticness", "instrumentalness", "loudness", "tempo"],
        fillcolor="rgb(29, 185, 84)",
        opacity=0.7,
        line=dict(color='darkgreen',width=3),
        fill="toself"
    ))
    fig.update_layout(
        polar = dict(
        bgcolor="rgba(0,0,0,0)",
        angularaxis = dict(
        direction = "clockwise",
        period = 6,
        tickcolor="white",
        tickfont_color="white")),
        title = {
                "text":"What are the specifics of the songs you listen to?",
                "x": 0.5,
                "xanchor":"center",
                "yanchor": "top",
                "font_size": 22}, 
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font_color="white",
        legend_font_color="white",
        width=1600,
        height=800
    )
    fig.update_polars(radialaxis_color="white") 
    fig.update_xaxes(color="white")
    fig.update_yaxes(color="white")
    return fig



