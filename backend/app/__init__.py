import os
from flask import Flask
from flask_cors import CORS

from .database import db
from .routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "skill-gap-secret-dev")
    database_url = os.getenv("DATABASE_URL", "sqlite:///skill_gap.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)

    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
