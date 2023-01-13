import json
import sqlite3
from flask import Flask, render_template, request
import uuid


def generate_uuid():
  return str(uuid.uuid4())

def read_file(file, unique_id):
    # Connect to the database
    conn = sqlite3.connect("spotify_db.db")

    # Create a cursor
    cursor = conn.cursor()

    # Execute a SELECT statement
    traffic = json.loads(file.read())
    
    # Upload records
    for record in traffic:     
        cursor.execute('INSERT INTO Streaming_data values(?,?,?,?,?)',[unique_id,
                                                                       record["endTime"], 
                                                                       record["artistName"], 
                                                                       record["trackName"], 
                                                                       record["msPlayed"]])
    # Commit the changes to the database
    conn.commit()

    # Close the connection to the database
    conn.close()

def upload_user(unique_id, name, age):
  # Connect to the database
  conn = sqlite3.connect("spotify_db.db")
  # Create a cursor
  cursor = conn.cursor()
  #Upload user
  cursor.execute('INSERT INTO Users values (?,?,?)', [unique_id,
                                                      name,
                                                      age])
  conn.commit()
  conn.close()


