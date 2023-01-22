from flask import Flask

# Initialize the app
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "a1b2ppp"
    app.config["UPLOAD_FOLDER"] = ""
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 #20MB
    app.config["ALLOWED_EXTENSIONS"] = [".json"]
    return app


