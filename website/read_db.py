import json
import sqlite3
from flask import Flask, render_template, request
import uuid

def generate_uuid():
  return str(uuid.uuid4())



def read_file(file):

    # Connect to the database
    conn = sqlite3.connect("spotify_db.db")

    # Create a cursor
    cursor = conn.cursor()

    # Execute a SELECT statement
    traffic = json.load(open(file))

    unique_id = generate_uuid()
    
    for record in traffic:     
        cursor.execute('INSERT INTO Streaming_data values(?,?,?,?,?)',[unique_id,
                                                                       record["endTime"], 
                                                                       record["artistName"], 
                                                                       record["trackName"], 
                                                                       record["msPlayed"]])
    #find you favourite artist
    #cursor.execute('SELECT artistName FROM Tracks GROUP BY artistName ORDER BY COUNT(*) DESC LIMIT 1;')
    #fav_artist = cursor.fetchall()
    return cursor

