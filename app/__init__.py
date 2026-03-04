from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.core.config import Config
from app.core.db_ext import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)

    # Register blueprints
    from app.module.auth.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.module.audit.audit_routes import audit_bp
    app.register_blueprint(audit_bp, url_prefix="/audit")
    from app.module.notification.notification_routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix="/notifications")
    from app.module.table.table_routes import table_bp
    app.register_blueprint(table_bp, url_prefix="/tables")

    return app
