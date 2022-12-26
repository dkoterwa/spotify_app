import sqlite3

# Connect to the database
conn = sqlite3.connect("spotify_db.db")

# Create a cursor
cursor = conn.cursor()

# Execute a SELECT statement
cursor.execute("SELECT * FROM Users")

# Fetch the results
results = cursor.fetchall()

# Loop through the results and print them
for row in results:
    print(row)


# Commit the changes
conn.commit()

# Close the connection
conn.close()