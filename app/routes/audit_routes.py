from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from ..schemas.audit_schema import AuditLogRequest, TableQuery
from ..services import audit_service

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/log", methods=["POST"])
@validate()
def create_log(body: AuditLogRequest):
    result, status = audit_service.create_log(body, ip=request.remote_addr)
    return jsonify(result), status


@audit_bp.route("/log/query", methods=["POST"])
@validate()
def get_logs(body: TableQuery):
    result, status = audit_service.get_logs(body)
    return jsonify(result.model_dump()), status
