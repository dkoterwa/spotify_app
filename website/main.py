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
    # Check if a file was uploaded
    if request.method == "POST":
        if "file" not in request.files:
            return "No file was uploaded"
        try:
            file = request.files["file"]
            extension = os.path.splitext(file.filename)[1]
            
            if file:
                if extension not in app.config["ALLOWED_EXTENSIONS"]:
                    return ".json is the only allowed file extension"

                else:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    cursor = read_file(file.filename)
                    name = request.form.get('text')
                    #print(f"xddddd {file.filename}")
                    #return "File uploaded successfully"
                    #return f"Hi {name}"
                    cursor.execute('SELECT artist_name FROM Streaming_data GROUP BY artist_name ORDER BY COUNT(*) DESC LIMIT 1;')
                    fav_artist = cursor.fetchall()
                    return render_template("home.html", name=name, fav_artist=fav_artist)
        except RequestEntityTooLarge:
           return "The file size is too large"



    # Check if the file has a valid filename
        if file.filename == "":
            return "Please select a file"

    # Save the file to the server
        
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
