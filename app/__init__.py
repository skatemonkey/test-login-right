from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    JWTManager(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app