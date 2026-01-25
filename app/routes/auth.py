from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

# =============================================================================
# TODO: Replace with database query
# This is hardcoded for testing purposes only.
# In production, retrieve user credentials from database.
# =============================================================================
USERS = {
    "admin": "admin123",
    "user": "user123",
}


def verify_user(username, password):
    """
    Verify user credentials.
    TODO: Replace with database lookup and proper password hashing (e.g., bcrypt)
    """
    if username in USERS and USERS[username] == password:
        return True
    return False


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    if not verify_user(username, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200
