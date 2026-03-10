from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager


def create_app():
    from app.core.config import Config
    from app.core.db_ext import db
    from app.core.redis_ext import init_redis

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)
    init_redis(app)

    # Register blueprints
    from app.module.auth.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.module.audit.audit_routes import audit_bp
    app.register_blueprint(audit_bp, url_prefix="/audit")
    from app.module.notification.notification_routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix="/notifications")
    from app.module.table.table_routes import table_bp
    app.register_blueprint(table_bp, url_prefix="/tables")
    from app.module.permission.permission_routes import permission_bp
    app.register_blueprint(permission_bp, url_prefix="/permissions")
    from app.module.user.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/users")

    return app
