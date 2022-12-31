import sqlite3
import pandas as pd
# Connect to the database
conn = sqlite3.connect("spotify_db.db")

# Create a cursor
cursor = conn.cursor()

# Read file with songs for recommender
file = pd.read_csv("/Volumes/HD/GitHub/spotify_app/spotify_data/playlists_data_to_recommend.csv")
#assert file != "", "Please provide path to the file with songs"

# Take columns
artist_name = file["artist"]
song_name = file["track_name"]
danceability = file["danceability"]
energy = file["energy"]
loudness = file["loudness"]
speechiness = file["speechiness"]
acousticness = file["acousticness"]
instrumentalness = file["instrumentalness"]
liveness = file["liveness"]
valence = file["valence"]
tempo = file["tempo"]
album = file["album"]
track_id = file["track_id"]

for i, row in file.iterrows():
# Upload to database
    conn.execute("INSERT INTO Recommender VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [row["artist"],
                                                                                row["track_name"],
                                                                                row["danceability"],
                                                                                row["energy"],
                                                                                row["loudness"],
                                                                                row["speechiness"],
                                                                                row["acousticness"],
                                                                                row["instrumentalness"],
                                                                                row["liveness"],
                                                                                row["valence"],
                                                                                row["tempo"],
                                                                                row["album"],
                                                                                row["track_id"]])
    conn.commit()
