
import json
import sqlite3
from flask import Flask, render_template, request

def read_file(file):

    # Connect to the database
    conn = sqlite3.connect("spotify_db.db")

    # Create a cursor
    cursor = conn.cursor()

    # Execute a SELECT statement
    cursor.execute('Create Table if not exists Tracks (trackName Text, artistName Text, albumName Text, trackUri Text)')
    traffic = json.load(open(file))
    columns = ['trackName','artistName','albumName','trackUri']
    for playlist in traffic['playlists']:
        for item in playlist['items']:
            row = item["track"]
            keys= tuple(row[c] for c in columns)
            cursor.execute('insert into Tracks values(?,?,?,?)',keys)
    #find you favourite artist
    # cursor.execute('SELECT artistName FROM Tracks GROUP BY artistName ORDER BY COUNT(*) DESC LIMIT 1;')
    # fav_artist = cursor.fetchall()
    return cursor

