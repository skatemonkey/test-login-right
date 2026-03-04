from flask import Blueprint
from flask_pydantic import validate
from app.common.schemas.auth_schema import LoginRequest
from app.module.auth import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
@validate()
def login(body: LoginRequest):
    result, status_code = auth_service.login(body)
    return result.model_dump(), status_code