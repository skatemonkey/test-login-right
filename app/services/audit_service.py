import json
from datetime import datetime
from ..models.audit_log import AuditLog
from ..models.user import User
from ..schemas.audit_schema import AuditLogRequest, TableQuery, AuditLogItem, PaginatedAuditLogResponse
from .. import db
from ..utils import pagination_utils

def create_log(req: AuditLogRequest, ip=str):
    details = req.details
    if isinstance(details, dict):
        details = json.dumps(details)

    log = AuditLog(
        user_id=req.userId,
        ip=ip,
        module=req.module,
        action=req.action,
        device=req.device,
        details=details
    )
    db.session.add(log)
    db.session.commit()

    return {"message": "logged"}, 201


def get_logs(query: TableQuery):
    q = db.session.query(AuditLog, User.username).join(User, AuditLog.user_id == User.user_id)

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
        'createdAt': AuditLog.created_time,
        'module': AuditLog.module,
        'action': AuditLog.action
    }
    q = pagination_utils.apply_sorting(q, query.sortField or 'createdAt', query.sortOrder or 'desc', field_map,
                                      AuditLog.created_time)

    # Paginate
    results, total, total_pages = pagination_utils.paginate(q, query.page, query.pageSize)

    # Map
    data = [map_audit_log(log, username) for log, username in results]

    return PaginatedAuditLogResponse(
        data=data,
        page=query.page,
        pageSize=query.pageSize,
        totalElements=total,
        totalPages=total_pages
    ), 200


# ============================================================
# Helper functions for get_logs
# ============================================================

def apply_audit_filters(q, filters):
    if not filters:
        return q
    if filters.module:
        q = q.filter(AuditLog.module == filters.module)
    if filters.action:
        q = q.filter(AuditLog.action == filters.action)
    if filters.dateFrom:
        date_from = datetime.strptime(filters.dateFrom, '%Y-%m-%d %H:%M:%S')
        q = q.filter(AuditLog.created_time >= date_from)
    if filters.dateTo:
        date_to = datetime.strptime(filters.dateTo, '%Y-%m-%d %H:%M:%S')
        q = q.filter(AuditLog.created_time <= date_to)
    return q


def map_audit_log(log, username):
    return AuditLogItem(
        id=log.id,
        username=username,
        ip=log.ip or '',
        device=log.device or '',
        createdAt=log.created_time.strftime('%Y-%m-%d %H:%M:%S') if log.created_time else '',
        module=log.module or '',
        action=log.action or '',
        details=log.details or ''
    )
