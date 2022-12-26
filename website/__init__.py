from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "a1b2ppp"
app.config["UPLOAD_FOLDER"] = ""

@app.route("/")
def welcome():
    return "Welcome stranger"

@app.route("/upload", methods=["POST", "GET"])
def upload_file():
    # Check if a file was uploaded
    if "file" not in request.files:
        return "No file was uploaded"

    file = request.files["file"]

    # Check if the file has a valid filename
    if file.filename == "":
        return "Please select a file"

    # Save the file to the server
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return "File uploaded successfully"