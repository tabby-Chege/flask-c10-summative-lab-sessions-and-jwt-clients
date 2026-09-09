from flask import Flask
from .config import Config
from .extensions import db, migrate, bcrypt, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @app.route("/")
    def index():
        return {"message": "Notes App API is running"}

    return app
