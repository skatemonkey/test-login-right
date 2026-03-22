from flask import Blueprint
from flask_pydantic import validate

from app.module.auth import auth_service
from app.shared.schemas.auth_schema import LoginRequest
from app.shared.utils import api_util

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
@validate()
def login(body: LoginRequest):
    result, status_code = auth_service.login(body)
    return api_util.api_response(result, status_code)
