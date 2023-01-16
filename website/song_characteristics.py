import sqlite3
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

def db_connect(database_name):
  # Connect to the database
  conn = sqlite3.connect(database_name)

  # Create a cursor
  cursor = conn.cursor()
  return conn, cursor

def connect_to_sp(cid, secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    return sp

def download_data(user_id, cursor):

    query = "SELECT end_time, artist_name, song_name, ms_played FROM Streaming_data WHERE UserID == '{}'".format(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    data_df = pd.DataFrame(data, columns=["end_time", "artist_name", "song_name", "ms_played"])
    data_df = data_df[data_df["end_time"].str.startswith("2022")]
    return data_df

def download_data_for_characteristics(user_id, cursor):

    query = "SELECT end_time, artist_name, song_name, ms_played FROM Streaming_data WHERE UserID == '{}'".format(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    data_df = pd.DataFrame(data, columns=["end_time", "artist_name", "song_name", "ms_played"])
    data_df = data_df[data_df["end_time"].str.startswith("2022")]
    data_df = data_df.drop_duplicates("song_name")
    data_df = data_df.head(int(len(data_df) * 0.5))
    return data_df

def get_general_statistics(dataframe):
    dataframe["min_played"] = dataframe["ms_played"]/60000
    total_listening_time = dataframe["min_played"].sum().astype(int) # Total listening time
    
    favorite_artists = dataframe.groupby("artist_name")["artist_name"].size().reset_index(name="count").sort_values("count", ascending=False) # Favorite artists
    favorite_songs = dataframe.groupby(["artist_name", "song_name"]).size().reset_index(name="count").sort_values("count", ascending=False) # Favorite songs
    distinct_artists = len(dataframe.drop_duplicates("artist_name")) # Distinct artists
    distinct_songs = len(dataframe.drop_duplicates("song_name")) # Distinct songs

    # Stats for favorite artist
    favorite_artists_minutes = dataframe.groupby("artist_name")["min_played"].sum().astype(int).reset_index(name="sum_of_minutes").sort_values("sum_of_minutes", ascending=False) # Minutes of favorite artists
    favorite_artist_fraction = np.round((favorite_artists_minutes["sum_of_minutes"].iloc[0] * 100 / favorite_artists_minutes["sum_of_minutes"][1:].sum()), 2) # Percentage of minutes occupied by favorite artist
    favorite_songs_of_fav_artist = favorite_songs[favorite_songs["artist_name"] == favorite_artists["artist_name"].iloc[0]] # Favorite songs of favorite artist
    number_of_songs_by_fav_artist = len(favorite_songs_of_fav_artist) # Number of distinct songs of favorite artist listened

    # Top morning and evening songs
    dataframe["hour"] = pd.to_datetime(dataframe["end_time"]).dt.hour
    dataframe_evening = dataframe[(dataframe["hour"].astype(int) > 19) | (dataframe["hour"].astype(int) < 5)]
    dataframe_morning = dataframe[(dataframe["hour"].astype(int) > 5) & (dataframe["hour"].astype(int) < 10)]
    favorite_evening = dataframe_evening.groupby(["artist_name", "song_name"]).size().reset_index(name="count").sort_values("count", ascending=False)[:5] # Favorite morning songs
    favorite_morning = dataframe_morning.groupby(["artist_name", "song_name"]).size().reset_index(name="count").sort_values("count", ascending=False)[:5] # Favorite evening songs

    return total_listening_time, favorite_artists, favorite_songs, distinct_artists, distinct_songs, favorite_artists_minutes, favorite_artist_fraction, favorite_songs_of_fav_artist, number_of_songs_by_fav_artist, favorite_morning, favorite_evening


def get_links(dataframe, sp):

    songs_links=[]
    # download links of songs
    for index, song in dataframe.iterrows():
        results = sp.search(q='artist:' + dataframe["artist_name"][index] + " track:" + dataframe["song_name"][index], type='track')
        items = results['tracks']['items']
    
        if len(items) != 0:
            try:
                link = items[1]['href']
            except:
                link = items[0]['href']
        else:
            link = ""
        
        print(link)
        songs_links.append(link)
       
    dataframe['song_url'] = songs_links
    dataframe_clear = dataframe[dataframe['song_url'] != ""] 
    
    return dataframe_clear

def get_features(dataframe, column, sp):
    
    links = []
    danceability = []
    energy = []
    loudness = []
    speechiness = []
    acousticness = [] 
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []

    for link in dataframe[column]:  
        
        connection = sp.audio_features(link)[0]
        
        if connection is not None:
            links.append(link)
            danceability.append(connection.get("danceability", None))
            energy.append(connection.get("energy", None))
            loudness.append(connection.get("loudness", None))
            speechiness.append(connection.get("speechiness", None))
            acousticness.append(connection.get("acousticness", None))
            instrumentalness.append(connection.get("instrumentalness", None))
            liveness.append(connection.get("liveness", None))
            valence.append(connection.get("valence", None))
            tempo.append(connection.get("tempo", None))
        else:
            links.append(None)
            danceability.append(None)
            energy.append(None)
            loudness.append(None)
            speechiness.append(None)
            acousticness.append(None)
            instrumentalness.append(None)
            liveness.append(None)
            valence.append(None)
            tempo.append(None)

    features_df = pd.DataFrame({"song_url": links,
                                "danceability": danceability,
                                "energy": energy,
                                "loudness": loudness,
                                "speechiness": speechiness,
                                "acousticness": acousticness,
                                "instrumentalness": instrumentalness,
                                "liveness": liveness,
                                "valence": valence,
                                "tempo": tempo})
    return features_df

def prepare_to_upload(dataframe, features):
    features = features.dropna()
    dataframe = dataframe.merge(features, on="song_url")
    dataframe = dataframe.drop(["song_url", "ms_played"], axis=1)
    return dataframe

def upload_characteristics_db(dataframe, conn, user_id):
    
    for i, row in dataframe.iterrows():
        conn.execute("INSERT INTO User_songs_info VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [user_id,
                                                                                      row["artist_name"],
                                                                                      row["song_name"],
                                                                                      row["danceability"],
                                                                                      row["energy"],
                                                                                      row["loudness"],
                                                                                      row["speechiness"],
                                                                                      row["acousticness"],
                                                                                      row["instrumentalness"],
                                                                                      row["liveness"],
                                                                                      row["valence"],
                                                                                      row["tempo"],
                                                                                      row["end_time"]
        ])

        conn.commit()





