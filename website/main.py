from __init__ import create_app
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from read_db import read_file, generate_uuid, upload_user
from datetime import datetime
from detailed_statistics import *
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
        unique_id = generate_uuid()
        user_name = request.form["name"]
        user_age = request.form["age"]
        upload_user(unique_id, user_name, user_age)

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
                        cursor = read_file(f.filename, unique_id) # Upload file to database
                    except RequestEntityTooLarge:
                            return "The file size is too large"
                    except Exception as e:
                        print("Error: ", e)

        return redirect(url_for("general_statistics"))
    else:
        return render_template("index.html")

@app.route('/general_statistics')
def general_statistics():
    df = px.data.medals_wide()
    fig1 = px.bar(df, x="nation", y=["gold", "silver", "bronze"])
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("general_statistics.html", graph1JSON=graph1JSON)

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
    return render_template('recommendations.html')

if __name__ == "__main__":
    app.run(debug=True)
