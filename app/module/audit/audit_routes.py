from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.audit import audit_service
from app.shared.schemas.audit_schema import AuditLogQuery, AuditLogRequest
from app.shared.utils import api_util

audit_bp = Blueprint("audit", __name__)


@audit_bp.post("/log")
@validate()
def create_log(body: AuditLogRequest):
    result, status = audit_service.create_log(body, ip=request.remote_addr)
    return api_util.api_response(result, status)


@audit_bp.post("/log/query")
@jwt_required()
@validate()
def get_logs(body: AuditLogQuery):
    result, status = audit_service.get_logs(body)
    return api_util.api_response(result, status)
