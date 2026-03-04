from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.permission import permission_service
from app.shared.schemas.permission_schema import (
    PermissionCreateRequest,
    PermissionListQuery,
    PermissionUpdateRequest,
)

permission_bp = Blueprint("permission", __name__)


@permission_bp.post("/query")
@jwt_required()
@validate()
def get_permissions(body: PermissionListQuery):
    result, status = permission_service.get_permissions(body)
    return jsonify(result.model_dump()), status


@permission_bp.get("/options")
@jwt_required()
@validate()
def get_filter_options():
    result, status = permission_service.get_options()
    return jsonify(result), status


@permission_bp.post("")
@jwt_required()
@validate()
def create_permission(body: PermissionCreateRequest):
    result, status = permission_service.create_permission(body)
    return jsonify(result), status


@permission_bp.put("/<int:permission_id>")
@jwt_required()
@validate()
def update_permission(permission_id: int, body: PermissionUpdateRequest):
    result, status = permission_service.update_permission(permission_id, body)
    return jsonify(result), status
