from __init__ import create_app
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from read_db import read_file
from datetime import datetime
import os

app = create_app()

@app.route("/", methods=["POST", "GET"])
def upload_file():

    if request.method == "POST":
        files = request.files.getlist("file")
        
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
                        cursor = read_file(f.filename) # Upload file to database
                        name = request.form.get('text')
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
