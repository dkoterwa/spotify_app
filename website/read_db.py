
import json
import sqlite3

# connection = sqlite3.connect('db.sqlite')
# cursor = connection.cursor()
# cursor.execute('Create Table if not exists Student (name Text, course Text, roll Integer)')
#
# traffic = json.load(open('json_file.json'))
# columns = ['name','course','roll']
# for row in traffic:
#     keys= tuple(row[c] for c in columns)
#     cursor.execute('insert into Student values(?,?,?)',keys)
#     print(f'{row["name"]} data inserted Succefully')
#
# connection.commit()
# connection.close()
#

# Connect to the database
conn = sqlite3.connect("spotify_db.db")

# Create a cursor
cursor = conn.cursor()

# Execute a SELECT statement
cursor.execute('Create Table if not exists Tracks (trackName Text, artistName Text, albumName Text, trackUri Text)')
traffic = json.load(open('play.json'))
#print(traffic["playlists"])
columns = ['trackName','artistName','albumName','trackUri']
for playlist in traffic['playlists']:
    for item in playlist['items']:
        row = item["track"]
        keys= tuple(row[c] for c in columns)
        cursor.execute('insert into Tracks values(?,?,?,?)',keys)
        print(f'{row["trackName"]} data inserted Succefully')

cursor.execute("SELECT trackName FROM Tracks")
print(cursor.fetchall())
# results = cursor.fetchall()
# print(results)
# conn.commit()
# conn.close()

# Fetch the results
# results = cursor.fetchall()

# Loop through the results and print them
# for row in results:
#     print(row)
#
#
# # Commit the changes
# conn.commit()
#
# # Close the connection
# conn.close()