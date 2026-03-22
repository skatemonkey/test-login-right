import json

from flask import has_request_context, request

from app.module.audit import audit_repository
from app.shared.schemas.audit_schema import AuditLogItem, AuditLogQuery, AuditLogRequest
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.utils import time as time_utils
from app.shared.utils import user_agent as user_agent_utils


def create_log(req: AuditLogRequest, ip: str | None = None):
    details = req.details
    if isinstance(details, dict):
        details = json.dumps(details)

    audit_repository.create_log(
        user_id=req.userId,
        ip=ip,
        module=req.module,
        action=req.action,
        device=user_agent_utils.summarize_device(req.device),
        details=details,
    )

    return None, 204


def create_log_internal(
    *,
    user_id: int,
    module: str,
    action: str,
    ip: str | None = None,
    device: str | None = None,
    details: str | None = None,
):
    if has_request_context():
        if ip is None:
            forwarded_for = request.headers.get("X-Forwarded-For")
            request_ip = (
                forwarded_for.split(",")[0].strip()
                if forwarded_for
                else request.remote_addr
            )
            ip = request_ip[:45] if request_ip else None
        if device is None:
            user_agent = request.headers.get("User-Agent")
            device = user_agent_utils.summarize_device(user_agent)

    audit_repository.create_log(
        user_id=user_id,
        ip=ip,
        module=module,
        action=action,
        device=user_agent_utils.summarize_device(device),
        details=details,
    )


def get_logs(query: AuditLogQuery):
    results, total, total_pages = audit_repository.query_logs(query)

    data = [_map_audit_log(log, username) for log, username in results]

    return PaginatedResponse[AuditLogItem](
        data=data,
        page=query.page,
        pageSize=query.pageSize,
        totalElements=total,
        totalPages=total_pages
    ), 200


def _map_audit_log(log, username):
    return AuditLogItem(
        id=log.id,
        username=username or "",
        ip=log.ip or "",
        device=log.device or "",
        createdAt=time_utils.format_datetime(log.created_at),
        module=log.module or "",
        action=log.action or "",
        details=log.details or "",
    )
