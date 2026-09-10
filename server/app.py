from flask import Flask

from .auth import auth_bp
from .config import Config
from .extensions import bcrypt, db, jwt, migrate
from .notes import notes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    @app.route("/")
    def index():
        return {"message": "Notes App API is running"}

    return app
