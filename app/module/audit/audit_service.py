from datetime import datetime
import json

from app.core import db
from app.shared.repository.audit_log import AuditLog
from app.shared.repository.user import User
from app.shared.schemas.audit_schema import AuditLogFilters, AuditLogItem, AuditLogQuery, AuditLogRequest
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.utils import pagination_utils


def create_log(req: AuditLogRequest, ip=str):
    details = req.details
    if isinstance(details, dict):
        details = json.dumps(details)

    log = AuditLog(
        user_id=req.user_id,
        ip=ip,
        module=req.module,
        action=req.action,
        device=req.device,
        details=details
    )
    db.session.add(log)
    db.session.commit()

    return {"message": "logged"}, 201


def get_logs(query: AuditLogQuery):
    q = db.session.query(AuditLog, User.username).outerjoin(User, AuditLog.user_id == User.user_id)

    # Search
    q = pagination_utils.apply_search(q, query.search, [
        User.username, AuditLog.module, AuditLog.action, AuditLog.ip, AuditLog.device
    ])

    # Filters
    q = apply_audit_filters(q, query.filters)

    # Sort
    field_map = {
        'id': AuditLog.id,
        'username': User.username,
        'ip': AuditLog.ip,
        'device': AuditLog.device,
        'created_at': AuditLog.created_at,
        'module': AuditLog.module,
        'action': AuditLog.action
    }
    q = pagination_utils.apply_sorting(q, query.sort_field or 'created_at', query.sort_order or 'desc', field_map,
                                       AuditLog.created_at)

    # Paginate
    results, total, total_pages = pagination_utils.paginate(q, query.page, query.page_size)

    # Map
    data = [map_audit_log(log, username) for log, username in results]

    return PaginatedResponse[AuditLogItem](
        data=data,
        page=query.page,
        page_size=query.page_size,
        total_elements=total,
        total_pages=total_pages
    ), 200


# ============================================================
# Helper functions for get_logs
# ============================================================

def apply_audit_filters(q, filters: AuditLogFilters | None):
    if not filters:
        return q
    if filters.module:
        q = q.filter(AuditLog.module == filters.module)
    if filters.action:
        q = q.filter(AuditLog.action == filters.action)
    if filters.date_from:
        date_from = datetime.strptime(filters.date_from, '%Y-%m-%d %H:%M:%S')
        q = q.filter(AuditLog.created_at >= date_from)
    if filters.date_to:
        date_to = datetime.strptime(filters.date_to, '%Y-%m-%d %H:%M:%S')
        q = q.filter(AuditLog.created_at <= date_to)
    return q


def map_audit_log(log, username):
    return AuditLogItem(
        id=log.id,
        username=username,
        ip=log.ip or '',
        device=log.device or '',
        created_at=log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
        module=log.module or '',
        action=log.action or '',
        details=log.details or ''
    )
