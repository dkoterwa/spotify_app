import sqlite3
import pandas as pd
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
    dataframe = dataframe.drop(["end_time", "song_url", "ms_played"], axis=1)
    return dataframe

def upload_characteristics_db(dataframe, conn, user_id):
    
    for i, row in dataframe.iterrows():
        conn.execute("INSERT INTO User_songs_info VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", [user_id,
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
        ])

        conn.commit()





