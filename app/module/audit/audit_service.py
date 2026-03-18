import json

from app.module.audit import audit_repository
from app.shared.schemas.audit_schema import AuditLogItem, AuditLogQuery, AuditLogRequest
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.utils import time as time_utils


def create_log(req: AuditLogRequest, ip=str):
    details = req.details
    if isinstance(details, dict):
        details = json.dumps(details)

    audit_repository.create_log(
        user_id=req.userId,
        ip=ip,
        module=req.module,
        action=req.action,
        device=req.device,
        details=details,
    )

    return {"message": "logged"}, 201


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
