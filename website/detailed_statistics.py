import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3

def get_user_stats():
    conn = sqlite3.connect("spotify_db.db")

    cursor = conn.cursor()

    cursor.execute("Select max(danceability), max(energy), max(acousticness), max(instrumentalness), max(loudness) from User_songs_info")
    records = cursor.fetchall()
    user_stats = records[0]
    print(user_stats)
    cursor.close()
    return user_stats
def get_song_stats():
    song_details = []
    conn = sqlite3.connect("spotify_db.db")
    cursor = conn.cursor()
   # cursor.execute("Select song_name, danceability from User_songs_info where danceability = (select max(danceability) from User_songs_info group by song_name)")
    cursor.execute("Select song_name, max(danceability) from User_songs_info")
    song_stats = cursor.fetchall()[0]
    song_details.append(song_stats)
    cursor.execute("Select song_name, max(energy) from User_songs_info")
    song_stats = cursor.fetchall()[0]
    song_details.append(song_stats)
    cursor.execute("Select song_name, max(acousticness) from User_songs_info")
    song_stats = cursor.fetchall()[0]
    song_details.append(song_stats)
    cursor.execute("Select song_name, max(instrumentalness) from User_songs_info")
    song_stats = cursor.fetchall()[0]
    song_details.append(song_stats)
    cursor.execute("Select song_name, loudness from User_songs_info where loudness = (select max(loudness) from User_songs_info group by song_name)")
    song_stats = cursor.fetchall()[0]
    song_details.append(song_stats)
    print(song_details)
    cursor.close()
    return song_details
def make_plot():
    stats = get_user_stats()
    stats = stats + stats
    fig = make_subplots(rows=2, cols=2, specs=[[{'type': 'polar'}]*2]*2)
    fig.add_trace(go.Scatterpolar(
          name = "Your songs with highest:",
          r = stats,
          theta = ["danceability", "energy", "accousticness", "instrumentalness", "loudness","danceability"],
        line_color="green",
        ), 1, 1)




    fig.update_traces(fill='toself')
    fig.update_layout(
        polar = dict(
          #radialaxis_angle = -45,
          angularaxis = dict(
            direction = "clockwise",
            period = 6)
        ),
    )
    fig.write_image("templates/fig1.webp")
    return 0
#fig.show()
