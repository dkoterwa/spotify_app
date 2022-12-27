import sqlite3
# Connect to the database
conn = sqlite3.connect("spotify_db.db")

# Create a cursor
cursor = conn.cursor()

# Check favorite artist
cursor.execute("SELECT * FROM Streaming_data")
query_fetch = cursor.fetchall()

print(query_fetch)