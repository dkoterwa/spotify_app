import sqlite3

# Connect to the database
conn = sqlite3.connect("spotify_db.db")

# Create a cursor
cursor = conn.cursor()

def download_characteristics(user_id):
    # Clear the table
    cursor.execute("SELECT * FROM Streaming_data WHERE UserID = " + user_id)
    return cursor

