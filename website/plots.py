import plotly.express as px
import plotly.io as pio
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def make_general_scatter(dataframe):
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

def make_general_heatmap(dataframe):
    color_stops = [[0, 'rgb(0,0,0)'], [0.25, 'rgb(0,68,27)'], [0.5, 'rgb(0,109,44)'], [0.75, 'rgb(255,255,191)'], [1, 'rgb(253,174,97)']]

    # Convert date
    dataframe['date'] = pd.to_datetime(dataframe['end_time'])
    dataframe['date'] = pd.to_datetime(dataframe['date'].dt.date)
    # Extract the hour and week from the datetime
    dataframe['hour'] = pd.to_datetime(dataframe['end_time']).dt.hour
    dataframe['week'] = pd.to_datetime(dataframe['end_time']).dt.week
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


def song_statistics_through_the_year(dataframe):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe['danceability'], y=dataframe['end_time'],
                        mode='lines',
                        name='danceability'))
    fig.add_trace(go.Scatter(x=dataframe['energy'], y=dataframe['end_time'],
                             mode='lines',
                             name='energy'))
    fig.add_trace(go.Scatter(x=dataframe['tempo'], y=dataframe['end_time'],
                             mode='lines',
                             name='tempo'))
    fig.add_trace(go.Scatter(x=dataframe['acousticness'], y=dataframe['end_time'],
                             mode='lines',
                             name='acousticnesss'))
    fig.add_trace(go.Scatter(x=dataframe['instrumentalness'], y=dataframe['end_time'],
                             mode='lines',
                             name='instrumentalness'))
    fig.show()
    return fig
