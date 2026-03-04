from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from flask_jwt_extended import jwt_required
from app.common.schemas.audit_schema import AuditLogRequest, TableQuery
from app.module.audit import audit_service

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
    result, status = audit_service.get_logs(body)
    return jsonify(result.model_dump()), status
