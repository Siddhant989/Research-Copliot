"""
app/__init__.py — Flask "app factory".

Why a factory?  Instead of creating the Flask app at module level (which
makes testing hard), we wrap it in a function.  Call create_app() once in
run.py and you get a fully configured Flask instance.
"""

from flask import Flask
from flask_cors import CORS
from config import config_map
import os


def create_app(env_name: str = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        env_name: "development" or "production".
                  Falls back to FLASK_ENV env var, then "development".
    """
    if env_name is None:
        env_name = os.getenv("FLASK_ENV", "development")

    # Flask uses the package name to locate templates/ and static/ folders
    app = Flask(__name__)

    # Load settings from config.py
    app.config.from_object(config_map[env_name])

    # Allow browser JavaScript (Cytoscape.js) to call our API endpoints
    CORS(app)

    # Register route blueprints (groups of related URLs)
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
