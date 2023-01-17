import sqlite3
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from tqdm import tqdm
import urllib.request

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

# Function to download user data from Streaming_data
def download_data(user_id, cursor):
    query = "SELECT end_time, artist_name, song_name, ms_played FROM Streaming_data WHERE UserID == '{}'".format(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    data_df = pd.DataFrame(data, columns=["end_time", "artist_name", "song_name", "ms_played"])
    data_df = data_df[data_df["end_time"].str.startswith("2022")]
    
    return data_df

# Function to download data from Streaming_data to upload characteristics for songs. Songs in outputed dataframe are unique and reduced (to make calculations faster)
def download_data_for_characteristics(user_id, cursor):
    query = "SELECT end_time, artist_name, song_name, ms_played FROM Streaming_data WHERE UserID == '{}'".format(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    data_df = pd.DataFrame(data, columns=["end_time", "artist_name", "song_name", "ms_played"])
    data_df = data_df[data_df["end_time"].str.startswith("2022")]
    data_df = data_df.drop_duplicates("song_name")
    data_df = data_df.head(int(len(data_df) * 0.01))

    return data_df

# Function to get songs with features from User_songs_info
def get_data_with_statistics(user_id, cursor):
    query = "SELECT artist_name, song_name, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, end_time FROM User_songs_info WHERE UserID == '{}'".format(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    data_df = pd.DataFrame(data, columns=["artist_name", "song_name", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "end_time"])
    data_df = data_df[data_df["end_time"].str.startswith("2022")]

    return data_df

# Function to get data dedicated for recommender
def get_data_from_recommender(cursor):
    query = "SELECT * FROM Recommender"
    cursor.execute(query)
    data = cursor.fetchall()
    data_df = pd.DataFrame(data, columns=["artist_name", "song_name", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "album", "track_id"])
    
    return data_df

# Function to get statistics needed for general statistics website section
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

# Function to get links from Spotify API for personal data
def get_links(dataframe, sp):
    songs_links=[]
    # download links of songs
    for index, song in tqdm(dataframe.iterrows()):
        results = sp.search(q='artist:' + dataframe["artist_name"][index] + " track:" + dataframe["song_name"][index], type='track')
        items = results['tracks']['items']
    
        if len(items) != 0:
            try:
                link = items[1]['href']
            except:
                link = items[0]['href']
        else:
            link = ""

        songs_links.append(link)
       
    dataframe['song_url'] = songs_links
    dataframe_clear = dataframe[dataframe['song_url'] != ""] 

    return dataframe_clear

# Get features for songs from personal data based on links downloaded earlier
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

    for link in tqdm(dataframe[column]):  

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

# Function to merge data with features 
def prepare_to_upload(dataframe, features):
    features = features.dropna()
    dataframe = dataframe.merge(features, on="song_url")
    dataframe = dataframe.drop(["song_url", "ms_played"], axis=1)

    return dataframe

# Function to upload data with features to database
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

# Function to get data with songs features from User_songs_info
def get_song_stats_by_date(user_id, cursor):
    print(user_id)
    query ="Select danceability, energy, tempo, acousticness, loudness, instrumentalness, end_time from User_songs_info where UserID =='{}'".format(user_id)
    cursor.execute(query)
    print(query)
    data = cursor.fetchall()
    print(data)
    data_frame = pd.DataFrame(cursor.fetchall(), columns=["danceability", "energy", "tempo", "acousticness", "loudness", "instrumentalness","end_time"])
    cursor.close()

    return data_frame

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
    df_personal = df_personal.sample(int(df_personal.shape[0]/3))
    df_recommender = df_recommender.sample(int(df_recommender.shape[0]/5))
    
    for i in tqdm(range (0, df_personal.shape[0])):
        for j in tqdm(range(0, df_recommender.shape[0])):

            distance = np.linalg.norm(df_personal[columns_for_vector].iloc[i, ].values - df_recommender[columns_for_vector].iloc[j, ].values)
    
            if all(distance < d for d in results_dict["distance"]) and df_personal["artist_name"].iloc[i] not in results_dict["artist_personal"] and df_recommender["song_name"].iloc[j] not in results_dict["song_database"]:            
                results_dict["song_personal"].append(df_personal["song_name"].iloc[i])
                results_dict["artist_personal"].append(df_personal["artist_name"].iloc[i])
                results_dict["artist_database"].append(df_recommender["artist_name"].iloc[j])
                results_dict["song_database"].append(df_recommender["song_name"].iloc[j])
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

        urllib.request.urlretrieve(artist_image_url_personal, "../website/static/artist_image_personal" + str(i) + ".jpg")
        urllib.request.urlretrieve(artist_image_url_recommender, "../website/static/artist_image_recommender" + str(i) + ".jpg")


    