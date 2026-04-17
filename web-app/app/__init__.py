"""
Initializes the Flask application and registers all blueprints for routing.
"""

from flask import Flask
from .routes import main


def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.register_blueprint(main)
    return app
