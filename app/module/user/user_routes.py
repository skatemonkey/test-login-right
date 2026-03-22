from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.user import user_service
from app.shared.schemas.user_schema import (
    UserCreateRequest,
    UserListQuery,
    UserPermissionToggleRequest,
    UserUpdateRequest,
)
from app.shared.utils import api_util

user_bp = Blueprint("users", __name__)


@user_bp.post("/query")
@jwt_required()
@validate()
def query_users(body: UserListQuery):
    result, status = user_service.query_users(body)
    return api_util.model_response(result, status)


@user_bp.get("/permission-matrix")
@jwt_required()
@validate()
def get_permission_matrix():
    result, status = user_service.get_permission_matrix()
    return api_util.model_response(result, status)


@user_bp.get("/<int:user_id>")
@jwt_required()
@validate()
def get_user(user_id: int):
    result, status = user_service.get_user_detail(user_id)
    return api_util.model_response(result, status)


@user_bp.post("")
@jwt_required()
@validate()
def create_user(body: UserCreateRequest):
    result, status = user_service.create_user(body)
    return api_util.model_response(result, status)


@user_bp.put("/<int:user_id>")
@jwt_required()
@validate()
def update_user(user_id: int, body: UserUpdateRequest):
    result, status = user_service.update_user(user_id, body)
    return api_util.model_response(result, status)


@user_bp.put("/<int:user_id>/permissions/<int:permission_id>")
@jwt_required()
@validate()
def toggle_user_permission(user_id: int, permission_id: int, body: UserPermissionToggleRequest):
    result, status = user_service.toggle_user_permission(
        user_id=user_id,
        permission_id=permission_id,
        enabled=body.enabled,
    )
    return api_util.model_response(result, status)
