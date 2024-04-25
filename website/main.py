from website import create_app
from flask import render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from website.read_db import read_file, generate_uuid, upload_user
from song_characteristics import get_song_stats_by_date_with_names, recommend_me, get_favorite_artist_photo, get_artists_photos, db_connect, connect_to_sp, get_general_statistics
from website.plots import make_general_scatter, make_general_heatmap, make_radar, song_statistics_through_the_year
from spot_secrets import cid, secret
import os
import json
import plotly
import pandas as pd
import numpy as np
RECOMMENDER_DATA_PATH = "../spotify_data/playlists_data_to_recommend.csv"

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
        
        print("database populated")
        return redirect(url_for("general_statistics"))
    else:
        return render_template("index.html")

@app.route('/general_statistics')
def general_statistics():
    sp = connect_to_sp(cid, secret)
    user_id = session.get("unique_id")
    print("ID", user_id)
    scatter = make_general_scatter(user_id) # Create scatterplot
    heatmap = make_general_heatmap(user_id) # Create heatmap
    graph1JSON = json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder) 
    graph2JSON = json.dumps(heatmap, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Get statistics
    general_statistics = get_general_statistics(user_id)
    get_favorite_artist_photo(general_statistics["favorite_artists"]["artist_name"].iloc[0], sp)
    return render_template("general_statistics.html", graph1JSON=graph1JSON, graph2JSON=graph2JSON, general_statistics=general_statistics)

@app.route('/detailed-info')
def detailed_info():
    user_id = session.get("unique_id")
    conn, cursor = db_connect("spotify_db3.db")
    # Create plots for user
    plot = song_statistics_through_the_year(user_id)
    plot2 = make_radar(user_id)
    graph3JSON = json.dumps(plot, cls=plotly.utils.PlotlyJSONEncoder)
    graph4JSON = json.dumps(plot2, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Download data for maximum statistics of user songs
    data_for_maxes = get_song_stats_by_date_with_names(user_id, cursor)
    cursor.execute("SELECT * FROM SONGS")
    songs_df = pd.DataFrame(cursor.fetchall(), columns=["song_id", "Artist_ID", "Song_name"])
    data_for_maxes = pd.merge(data_for_maxes, songs_df, on="song_id")

    # Generate statistics
    max_danceability = data_for_maxes[data_for_maxes["danceability"] == np.max(data_for_maxes["danceability"])].iloc[0]
    max_energy = data_for_maxes[data_for_maxes["energy"] == np.max(data_for_maxes["energy"])].iloc[0]
    max_tempo = data_for_maxes[data_for_maxes["tempo"] == np.max(data_for_maxes["tempo"])].iloc[0]
    max_loudness = data_for_maxes[data_for_maxes["loudness"] == np.max(data_for_maxes["loudness"])].iloc[0]
    max_instrumental = data_for_maxes[data_for_maxes["instrumentalness"] == np.max(data_for_maxes["instrumentalness"])].iloc[0]
    max_acoustic = data_for_maxes[data_for_maxes["acousticness"] == np.max(data_for_maxes["acousticness"])].iloc[0]
    maxes_df = pd.DataFrame([max_danceability, max_energy, max_tempo, max_loudness, max_instrumental, max_acoustic], columns = ['artist_name', "Song_name", "danceability", "energy", "tempo", "acousticness", "loudness", "instrumentalness"])
    feature_list = ["danceability", "energy", "tempo", "acousticness", "loudness", "instrumentalness"]

    return render_template('detailed_information.html', graph3JSON=graph3JSON, graph4JSON=graph4JSON, maxes_df=maxes_df, feature_list=feature_list)

@app.route('/recommendations')
def recommendations():
    user_id = session.get("unique_id")
    _, cursor = db_connect("spotify_db3.db")
    sp = connect_to_sp(cid, secret)
    data_personal = get_song_stats_by_date_with_names(user_id, cursor)
    cursor.execute("SELECT * FROM SONGS")
    songs_df = pd.DataFrame(cursor.fetchall(), columns=["song_id", "Artist_ID", "Song_name"])
    personal_data = pd.merge(data_personal, songs_df, on="song_id")
    
    recommender_data = pd.read_csv(RECOMMENDER_DATA_PATH, index_col=0)
    recommender_results = recommend_me(personal_data, recommender_data, ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
    get_artists_photos(recommender_results, sp)
    return render_template("recommendations.html", recommender_results=recommender_results, zip=zip)

if __name__ == "__main__":
    app.run(debug=True)
