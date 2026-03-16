from datetime import datetime

from app.core import db
from app.shared.model.audit_log import AuditLog
from app.shared.model.user import User
from app.shared.schemas.audit_schema import AuditLogFilters, AuditLogQuery
from app.shared.utils import db_session_utils, pagination_utils


def create_log(
    *,
    user_id: int,
    ip: str | None,
    module: str | None,
    action: str | None,
    device: str | None,
    details: str | None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        ip=ip,
        module=module,
        action=action,
        device=device,
        details=details,
    )
    db.session.add(log)
    db_session_utils.commit_session()
    return log


def query_logs(query: AuditLogQuery):
    log_query = (
        db.session.query(AuditLog, User.username)
        .outerjoin(User, AuditLog.user_id == User.user_id)
    )

    log_query = pagination_utils.apply_search(
        log_query,
        query.search,
        [User.username, AuditLog.module, AuditLog.action, AuditLog.ip, AuditLog.device],
    )
    log_query = _apply_audit_filters(log_query, query.filters)

    field_map = {
        "id": AuditLog.id,
        "username": User.username,
        "ip": AuditLog.ip,
        "device": AuditLog.device,
        "createdAt": AuditLog.created_at,
        "module": AuditLog.module,
        "action": AuditLog.action,
    }
    log_query = pagination_utils.apply_sorting(
        log_query,
        query.sortField or "createdAt",
        query.sortOrder or "desc",
        field_map,
        AuditLog.created_at,
    )

    return pagination_utils.paginate(log_query, query.page, query.pageSize)


def _apply_audit_filters(log_query, filters: AuditLogFilters | None):
    if not filters:
        return log_query

    if filters.module:
        log_query = log_query.filter(AuditLog.module == filters.module)
    if filters.action:
        log_query = log_query.filter(AuditLog.action == filters.action)
    if filters.dateFrom:
        log_query = log_query.filter(
            AuditLog.created_at >= datetime.strptime(filters.dateFrom, "%Y-%m-%d %H:%M:%S"),
        )
    if filters.dateTo:
        log_query = log_query.filter(
            AuditLog.created_at <= datetime.strptime(filters.dateTo, "%Y-%m-%d %H:%M:%S"),
        )

    return log_query
