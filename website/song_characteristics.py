import sqlite3
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from tqdm import tqdm
import urllib.request
import time
from spot_secrets import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Function to connect with database
def db_connect(database_name):
  # Connect to the database
  conn = sqlite3.connect(database_name)
  # Create a cursor
  cursor = conn.cursor()
  
  return conn, cursor

# Function to connect to spotify API
def connect_to_sp(cid, secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    return sp

# Function to get data with songs features from User_songs_info
def get_song_stats_by_date(user_id, cursor):
    cursor.execute("SELECT a.end_Time, b.* FROM Streaming_data a JOIN Songs_features b ON a.Song_ID = b.Song_ID WHERE User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()
    dataframe = pd.DataFrame(data, columns=["end_time", "song_id", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
    dataframe = normalize(dataframe, ["tempo", "loudness"])
    dataframe = dataframe[dataframe["end_time"].str.startswith("2022")]
    return dataframe

# Function to get data with songs features from User_songs_info but also with artist and song name
def get_song_stats_by_date_with_names(user_id, cursor):
    cursor.execute("SELECT a.end_Time, a.Artist_ID, b.* FROM Streaming_data a JOIN Songs_features b ON a.Song_ID = b.Song_ID WHERE User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()
    dataframe = pd.DataFrame(data, columns=["end_time", "Artist_ID","song_id", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
    dataframe = normalize(dataframe, ["tempo", "loudness"])
    cursor.execute("SELECT * FROM Artists")
    artists = cursor.fetchall()
    artists_dataframe = pd.DataFrame(artists, columns=["Artist_ID", "artist_name"])
    final_df = pd.merge(dataframe, artists_dataframe, on="Artist_ID")
    return final_df


# Function to get statistics needed for general statistics website section
def get_general_statistics(user_id):
    conn, cursor = db_connect("spotify_db3.db")
    cursor.execute("SELECT a.*, b.Song_name, c.Artist_name FROM Streaming_data a INNER JOIN Songs b ON a.Song_ID = b.Song_ID INNER JOIN Artists c ON b.Artist_ID = c.Artist_ID WHERE a.User_ID = '{}' ".format(user_id))
    data = cursor.fetchall()
    dataframe = pd.DataFrame(data, columns = ["User_ID", "Song_ID", "Artist_ID", "end_time", "ms_played", "song_name", "artist_name"])

    dataframe= dataframe[dataframe["end_time"].str.startswith("2022")]
    dataframe['ms_played'] = dataframe["ms_played"].astype(int)  
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

# Function to get links from Spotify API for personal data
def get_audio_features(df, cid, secret):
    # Create the Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Create columns for each feature
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    for feature in features:
        df[feature] = None
    # Iterate through each row of the DataFrame
    for i, row in tqdm(df.iterrows()):
        artist = row['artistName']
        track_name = row['trackName']
        try:
            # Search for the track
            results = sp.search(q=f'track:{track_name} artist:{artist}', type='track')
            track_id = results['tracks']['items'][0]['id']
            # Retrieve the track's audio features
            audio_features = sp.audio_features(track_id)
            # Populate the corresponding feature column in the DataFrame
            for feature in features:
                df.at[i, feature] = audio_features[0][feature]
        except:
            print(f"No data found for {artist} - {track_name}")
    return df


# Function to merge data with features 
def prepare_to_upload(dataframe, features):
    features = features.dropna()
    dataframe = dataframe.merge(features, on="song_url")
    dataframe = dataframe.drop(["song_url", "msPlayed"], axis=1)

    return dataframe

# Function to normalize features which are not yet normalized
def normalize(df, columns):
    result = df.copy()
    for feature_name in columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)

    return result

# Function to recommend dictionary with songs from table with recommender database
def recommend_me(df_personal, df_recommender, columns_for_vector):
    results_dict = {"artist_personal":[],
                                "song_personal":[],
                                "artist_database":[],
                                "song_database":[],
                                "distance":[]}

    df_personal = normalize(df_personal, ["loudness", "tempo"])
    df_recommender = normalize(df_recommender, ["loudness", "tempo"])    
    rows_to_drop = df_recommender[df_recommender["track_name"].isin(df_personal["Song_name"])].index
    df_recommender = df_recommender.drop(rows_to_drop)
    df_personal = df_personal.sample(int(df_personal.shape[0]/20))
    df_recommender = df_recommender.sample(int(df_recommender.shape[0]/5))

    
    for i in tqdm(range (0, df_personal.shape[0])):
        for j in tqdm(range(0, df_recommender.shape[0])):

            distance = np.linalg.norm(df_personal[columns_for_vector].iloc[i, ].values - df_recommender[columns_for_vector].iloc[j, ].values)
    
            if all(distance < d for d in results_dict["distance"]) and df_personal["artist_name"].iloc[i] not in results_dict["artist_personal"] and df_recommender["track_name"].iloc[j] not in results_dict["song_database"] and df_recommender["artist"].iloc[j] not in results_dict["artist_database"] and df_recommender["track_name"].iloc[j] not in df_personal["Song_name"]:            
                results_dict["song_personal"].append(df_personal["Song_name"].iloc[i])
                results_dict["artist_personal"].append(df_personal["artist_name"].iloc[i])
                results_dict["artist_database"].append(df_recommender["artist"].iloc[j])
                results_dict["song_database"].append(df_recommender["track_name"].iloc[j])
                results_dict["distance"].append(distance)

            if len(results_dict["distance"]) > 5:
                lowest_value = min(results_dict["distance"])
                lowest_index = results_dict["distance"].index(lowest_value)
                
                for key in results_dict:
                    results_dict[key].pop(lowest_index)
                
    return results_dict

# Get photo of favorite artist for general statistics
def get_favorite_artist_photo(artist_name, sp):
    result = sp.search(q=artist_name, type="artist")
    artist_id = result["artists"]["items"][0]["id"]
    artist_search = sp.artist(artist_id)
    artist_image_url = artist_search["images"][0]["url"]
    
    urllib.request.urlretrieve(artist_image_url, "../website/static/favorite_artist_photo.jpg")

# Get photos for personal and recommended songs and save them in static folder
def get_artists_photos(results_dict, sp):
    for i in tqdm(range(len(results_dict))):
        artist_personal_name = results_dict["artist_personal"][i]
        artist_recommender_name = results_dict["artist_database"][i]
        result_personal = sp.search(q=artist_personal_name, type='artist')
        artist_id_personal = result_personal['artists']['items'][0]['id']
        result_recommender = sp.search(q=artist_recommender_name, type='artist')
        artist_id_recommender = result_recommender['artists']['items'][0]['id']
        artist_search_personal = sp.artist(artist_id_personal)
        artist_search_recommender = sp.artist(artist_id_recommender)
        artist_image_url_personal = artist_search_personal['images'][0]['url']
        artist_image_url_recommender = artist_search_recommender['images'][0]['url']

        urllib.request.urlretrieve(artist_image_url_personal, "../website/static/photos_personal/artist_image_personal" + str(i) + ".jpg")
        urllib.request.urlretrieve(artist_image_url_recommender, "../website/static/photos_recommender/artist_image_recommender" + str(i) + ".jpg")


    