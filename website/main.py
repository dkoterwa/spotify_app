from __init__ import create_app
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from read_db import read_file, generate_uuid, upload_user
from datetime import datetime
import os
import uuid

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
                        f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename)) # Save file
                        cursor = read_file(f.filename, unique_id) # Upload file to database
                        name = request.form.get("name")
                    except RequestEntityTooLarge:
                            return "The file size is too large"
                    except Exception as e:
                        print("Error: ", e)

        cursor.execute('SELECT artist_name FROM Streaming_data GROUP BY artist_name ORDER BY COUNT(*) DESC LIMIT 1;')
        fav_artist = cursor.fetchall()
        return render_template("home.html", name=name, fav_artist=fav_artist)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
