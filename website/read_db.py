import json
import sqlite3
import uuid
import pandas as pd
from spot_secrets import cid, secret
from song_characteristics import get_audio_features

# Function to generate unique id
def generate_uuid():
  return str(uuid.uuid4())

# Function to populate database with uploaded files
def read_file(file, user_id):
    # Connect to the database
    conn = sqlite3.connect("spotify_db3.db")
    cursor = conn.cursor()
    data = json.loads(file.read())
    dataframe = pd.DataFrame(data)

    # Upload records
    for index, row in dataframe.iterrows():
        artist_name = row["artistName"]
        cursor.execute("SELECT Artist_ID FROM Artists WHERE Artist_name == ?", (artist_name,))
        artist_id = cursor.fetchone()
        if artist_id is not None: # Artist already in the database
            artist_id = artist_id[0] 
        if artist_id is None: 
            artist_id = generate_uuid()
            cursor.execute("INSERT INTO Artists (Artist_ID, Artist_name) VALUES(?,?)", (artist_id, artist_name))
            
        song_name = row["trackName"]
        cursor.execute("SELECT Song_ID FROM Songs WHERE Song_name == ?", (song_name,))
        song_id = cursor.fetchone()
        
        if song_id is not None: # Song already in the database
            song_id = song_id[0]
        if song_id is None: 
            song_id = generate_uuid()
            cursor.execute("INSERT INTO Songs (Song_ID, Artist_ID, Song_name) VALUES(?,?,?)", (str(song_id), str(artist_id), row["trackName"]))
    conn.commit()
                                                                                                                                                                                                                
    cursor.execute("SELECT * FROM Songs")
    songs_table = pd.DataFrame(cursor.fetchall(), columns=["Song_ID", "Artist_ID", "Song_name"])
    cursor.execute("SELECT * FROM Artists")
    artists_table = pd.DataFrame(cursor.fetchall(), columns=["Artist_ID", "Artist_name"])
    combined_table= pd.merge(artists_table, songs_table, on="Artist_ID")
    data_final = dataframe.merge(combined_table, left_on=["artistName","trackName"], right_on=["Artist_name","Song_name"])

    for index, row in data_final.iterrows():
        cursor.execute("INSERT INTO Streaming_data (User_ID, Song_ID, Artist_ID, end_Time, ms_Played) VALUES (?,?,?,?,?)",(str(user_id), row["Song_ID"], row["Artist_ID"],row["endTime"],row["msPlayed"]))

    # Upload data to Songs_features table (uploading only 10% of songs in order to save time)                                 
    dataframe_without_duplicates = dataframe.drop_duplicates("trackName")
    dataframe_without_duplicates = dataframe_without_duplicates.head(int(len(dataframe_without_duplicates) * 0.1))   
    dataframe_without_duplicates = get_audio_features(dataframe_without_duplicates, cid, secret)
    merged_df_no_duplicates = pd.merge(dataframe_without_duplicates, songs_table, left_on='trackName', right_on='Song_name')
    song_id = merged_df_no_duplicates["Song_ID"]
    merged_df_no_duplicates.dropna(inplace=True)
    
    for index, row in merged_df_no_duplicates.iterrows():
        cursor.execute("SELECT Song_ID FROM Songs_features WHERE Song_ID == ?", (song_id.iloc[index],))
        song_id_check = cursor.fetchone()
        if song_id_check is None:
            cursor.execute("INSERT INTO Songs_features (Song_ID, Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo) VALUES (?,?,?,?,?,?,?,?,?,?)", (song_id.iloc[index], 
                                                                                                                                                                                                        row["danceability"],
                                                                                                                                                                                                        row["energy"],
                                                                                                                                                                                                        row["loudness"],
                                                                                                                                                                                                        row["speechiness"],
                                                                                                                                                                                                        row["acousticness"],
                                                                                                                                                                                                        row["instrumentalness"],
                                                                                                                                                                                                        row["liveness"],
                                                                                                                                                                                                        row["valence"],
                                                                                                                                                                                                        row["tempo"]))
    conn.commit()
    conn.close()

# Function to upload user to database
def upload_user(unique_id, name, age):
  conn = sqlite3.connect("spotify_db3.db")
  cursor = conn.cursor()
  cursor.execute('INSERT INTO Users values (?,?,?)', [unique_id,
                                                      name,
                                                      age])
  conn.commit()
  conn.close()


