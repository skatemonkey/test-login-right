from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config.config import Config
from app.extensions.db_ext import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.routes.audit_routes import audit_bp
    app.register_blueprint(audit_bp, url_prefix="/audit")

    return app