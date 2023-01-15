from __init__ import create_app
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from read_db import read_file, generate_uuid, upload_user
from datetime import datetime
from detailed_statistics import *
from song_characteristics import *
from plots import *
from webscrapping import *
import os
import uuid
import json
import plotly
import plotly.express as px

app = create_app()


@app.route("/", methods=["POST", "GET"])

def upload_file():
    if request.method == "POST":

        files = request.files.getlist("file")
        session["unique_id"] = generate_uuid()
        user_name = request.form["name"]
        user_age = request.form["age"]
        upload_user(session["unique_id"], user_name, user_age)

        for f in files: 
            if not f.filename: # Check if user uploaded any file
                return "No file was uploaded"
            
            extension = os.path.splitext(f.filename)[1]
            if f:
                if extension not in app.config["ALLOWED_EXTENSIONS"]: # Check extension
                    return ".json is the only allowed file extension"
                else:
                    try:
                        filename = secure_filename(f.filename)
                        cursor = read_file(f, session["unique_id"]) # Upload file to database
                    except RequestEntityTooLarge:
                            return "The file size is too large"
                    except Exception as e:
                        print("Error: ", e)

        return redirect(url_for("general_statistics"))
    else:
        return render_template("index.html")

@app.route('/general_statistics')
def general_statistics():
    user_id = session.get("unique_id")
    conn, cursor = db_connect("spotify_db.db")
    data = download_data(user_id, cursor)
    scatter = make_general_scatter(data)
    heatmap = make_general_heatmap(data)
    graph1JSON = json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(heatmap, cls=plotly.utils.PlotlyJSONEncoder)
    total_listening_time, favorite_artists, favorite_songs, distinct_artists, distinct_songs, favorite_artists_minutes, favorite_artist_fraction, favorite_songs_of_fav_artist, number_of_songs_by_fav_artist, favorite_morning, favorite_evening = get_general_statistics(data)

    fav_artist_link = [get_main_wiki_image(i) for i in favorite_artists["artist_name"][:5]]
    return render_template("general_statistics.html", graph1JSON=graph1JSON, graph2JSON=graph2JSON, total_listening_time = total_listening_time, favorite_artists = favorite_artists, favorite_songs = favorite_songs, distinct_artists = distinct_artists, distinct_songs = distinct_songs, favorite_artists_minutes = favorite_artists_minutes, favorite_artist_fraction = favorite_artist_fraction, favorite_songs_of_fav_artist = favorite_songs_of_fav_artist, number_of_songs_by_fav_artist = number_of_songs_by_fav_artist, favorite_morning = favorite_morning, favorite_evening = favorite_evening, fav_artist_link=fav_artist_link, zip=zip)

@app.route('/detailed-info')
def detailed_info():
    song_stats=get_song_stats()
    make_plot()
    song1 = song_stats[1]
    descriptions = [
        "dancebility",
        "energy",
        "acoustniess",
        "instrumentalness",
        "loudness"
    ]
    song_formatted = [f" {descr} being {song2} is {song1}" for (song1, song2), descr in zip(song_stats, descriptions)]
    return render_template('detailed_information.html', song_stats=song_formatted, song1=song1)

@app.route('/recommendations')
def recommendations():
    user_id = session.get("unique_id")
    conn, cursor = db_connect("spotify_db.db")
    data = download_data(user_id, cursor)
    favorite_artists = get_general_statistics(data)[1]
    fav_artist_link = [get_main_wiki_image(i) for i in favorite_artists["artist_name"][:5]]
    return render_template('recommendations.html',favorite_artists = favorite_artists, fav_artist_link=fav_artist_link, zip=zip)

if __name__ == "__main__":
    app.run(debug=True)
