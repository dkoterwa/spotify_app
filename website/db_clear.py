import sqlite3

# Connect to the database
conn = sqlite3.connect("spotify_db3.db")

# Create a cursor
cursor = conn.cursor()

# Clear the table
cursor.execute("DELETE FROM Streaming_data")

# Commit the changes to the database
conn.commit()

# Close the connection to the database
conn.close()