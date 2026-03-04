from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from flask_jwt_extended import jwt_required
from ..schemas.audit_schema import AuditLogRequest, TableQuery
from ..services import audit_service
from ..utils.auth_utils import resolve_current_user_id

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/log", methods=["POST"])
@jwt_required()
@validate()
def create_log(body: AuditLogRequest):
    current_user_id = resolve_current_user_id()
    if current_user_id is None:
        return jsonify({"error": "Invalid access token"}), 401
    if body.userId != current_user_id:
        return jsonify({"error": "Forbidden: userId does not match token"}), 403

    result, status = audit_service.create_log(body, ip=request.remote_addr)
    return jsonify(result), status


@audit_bp.route("/log/query", methods=["POST"])
@jwt_required()
@validate()
def get_logs(body: TableQuery):
    result, status = audit_service.get_logs(body)
    return jsonify(result.model_dump()), status
