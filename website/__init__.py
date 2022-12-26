from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "a1b2ppp"
    app.config["UPLOAD_FOLDER"] = ""
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024 #4MB
    app.config["ALLOWED_EXTENSIONS"] = [".json"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spotify.db"
    return app


