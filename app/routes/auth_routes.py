from flask import Blueprint, jsonify
from flask_pydantic import validate
from ..schemas.auth_schema import LoginRequest
from ..services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
@validate()
def login(body: LoginRequest):
    result, status = auth_service.login(body)
    return jsonify(result.model_dump()), status