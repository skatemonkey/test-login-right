from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.permission import permission_service
from app.shared.schemas.permission_schema import (
    PermissionCreateRequest,
    PermissionListQuery,
    PermissionUpdateRequest,
)
from app.shared.utils import api_util

permission_bp = Blueprint("permission", __name__)


@permission_bp.post("/query")
@jwt_required()
@validate()
def get_permissions(body: PermissionListQuery):
    result, status = permission_service.get_permissions(body)
    return api_util.model_response(result, status)


@permission_bp.post("")
@jwt_required()
@validate()
def create_permission(body: PermissionCreateRequest):
    result, status = permission_service.create_permission(body)
    return api_util.model_response(result, status)


@permission_bp.put("/<int:permission_id>")
@jwt_required()
@validate()
def update_permission(permission_id: int, body: PermissionUpdateRequest):
    result, status = permission_service.update_permission(permission_id, body)
    return api_util.model_response(result, status)
