from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "a1b2ppp"

    return app