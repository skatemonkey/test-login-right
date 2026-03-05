from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.audit import audit_service
from app.shared.schemas.audit_schema import AuditLogQuery, AuditLogRequest

audit_bp = Blueprint("audit", __name__)


@audit_bp.post("/log")
@validate()
def create_log(body: AuditLogRequest):
    result, status = audit_service.create_log(body, ip=request.remote_addr)
    return jsonify(result), status


@audit_bp.post("/log/query")
@jwt_required()
@validate()
def get_logs(body: AuditLogQuery):
    result, status = audit_service.get_logs(body)
    return jsonify(result.model_dump()), status
