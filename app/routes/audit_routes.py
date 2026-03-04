from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from flask_jwt_extended import jwt_required
from ..schemas.audit_schema import AuditLogRequest, TableQuery
from ..services import audit_service
from ..utils.auth_utils import resolve_current_user_id

audit_bp = Blueprint("audit", __name__)


@audit_bp.post("/log")
@validate()
def create_log(body: AuditLogRequest):
    result, status = audit_service.create_log(body, ip=request.remote_addr)
    return jsonify(result), status


@audit_bp.post("/log/query")
@jwt_required()
@validate()
def get_logs(body: TableQuery):
    current_user_id = resolve_current_user_id()
    if current_user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    result, status = audit_service.get_logs(body)
    return jsonify(result.model_dump()), status
