from __init__ import create_app
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from read_db import read_file, generate_uuid, upload_user
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from datetime import datetime
from detailed_statistics import *
from song_characteristics import *
from plots import *
from webscrapping import *
from spot_secrets import *
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
    sp = connect_to_sp(cid, secret)
    data = download_data(user_id, cursor)
    scatter = make_general_scatter(data)
    heatmap = make_general_heatmap(data)
    graph1JSON = json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(heatmap, cls=plotly.utils.PlotlyJSONEncoder)
    total_listening_time, favorite_artists, favorite_songs, distinct_artists, distinct_songs, favorite_artists_minutes, favorite_artist_fraction, favorite_songs_of_fav_artist, number_of_songs_by_fav_artist, favorite_morning, favorite_evening = get_general_statistics(data)
    get_favorite_artist_photo(favorite_artists["artist_name"].iloc[0], sp)

    fav_artist_link = [get_main_wiki_image(i) for i in favorite_artists["artist_name"][:5]]
    return render_template("general_statistics.html", graph1JSON=graph1JSON, graph2JSON=graph2JSON, total_listening_time = total_listening_time, favorite_artists = favorite_artists, favorite_songs = favorite_songs, distinct_artists = distinct_artists, distinct_songs = distinct_songs, favorite_artists_minutes = favorite_artists_minutes, favorite_artist_fraction = favorite_artist_fraction, favorite_songs_of_fav_artist = favorite_songs_of_fav_artist, number_of_songs_by_fav_artist = number_of_songs_by_fav_artist, favorite_morning = favorite_morning, favorite_evening = favorite_evening, fav_artist_link=fav_artist_link, zip=zip)

@app.route('/detailed-info')
def detailed_info():

    user_id = session.get("unique_id")
    conn, cursor = db_connect("spotify_db.db")
    feautures_data = get_song_stats_by_date(user_id, cursor)
    data = download_data_for_characteristics(user_id, cursor)

    sp = connect_to_sp(cid, secret)
    df_links = get_links(data, sp)
    features = get_features(data, "song_url", sp)
    data_prep = prepare_to_upload(df_links, features)

    upload_characteristics_db(data_prep, conn, user_id)
    plot = song_statistics_through_the_year(feautures_data)
    graph3JSON = json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder)
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
    return render_template('detailed_information.html', song_stats=song_formatted, song1=song1, graph3=graph3JSON)

@app.route('/recommendations')
def recommendations():
    user_id = session.get("unique_id")
    conn, cursor = db_connect("spotify_db.db")
    
    personal_data = get_data_with_statistics("fd3d877b-6d54-4cba-a037-ed9ab548f8af", cursor)
    recommender_data = get_data_from_recommender(cursor)
    recommender_results = recommend_me(personal_data, recommender_data, ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])

    data = download_data(user_id, cursor)
    favorite_artists = get_general_statistics(data)[1]
    fav_artist_link = [get_main_wiki_image(i) for i in favorite_artists["artist_name"][:5]]
    return render_template('recommendations.html',favorite_artists = favorite_artists, fav_artist_link=fav_artist_link, recommender_results=recommender_results, zip=zip)

if __name__ == "__main__":
    app.run(debug=True)
