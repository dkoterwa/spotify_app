import sqlite3
# Connect to the database
conn = sqlite3.connect("spotify_db3.db")

# Create a cursor
cursor = conn.cursor()

# Check Streaming_data table
cursor.execute("SELECT * FROM Streaming_data")
query_fetch = cursor.fetchall()

print(query_fetch)