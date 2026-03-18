from app.core.db_ext import db
from app.shared.model.permission import Permission
from app.shared.schemas.permission_schema import PermissionFilters, PermissionListQuery
from app.shared.utils import db_session_utils, pagination_utils


def get_permissions(query: PermissionListQuery):
    permission_query = Permission.query
    permission_query = pagination_utils.apply_search(
        permission_query,
        query.search,
        [Permission.module, Permission.action, Permission.description],
    )
    permission_query = _apply_permission_filters(permission_query, query.filters)

    field_map = {
        "permissionId": Permission.permission_id,
        "module": Permission.module,
        "action": Permission.action,
        "description": Permission.description,
        "isActive": Permission.is_active,
        "createdAt": Permission.created_at,
        "updatedAt": Permission.updated_at,
    }
    permission_query = pagination_utils.apply_sorting(
        permission_query,
        query.sortField or "updatedAt",
        query.sortOrder or "desc",
        field_map,
        Permission.updated_at,
    )

    return pagination_utils.paginate(permission_query, query.page, query.pageSize)


def get_permission_by_id(permission_id: int) -> Permission | None:
    return Permission.query.filter_by(permission_id=permission_id).first()


def get_permission_by_module_and_action(
    module: str,
    action: str,
    *,
    exclude_permission_id: int | None = None,
) -> Permission | None:
    permission_query = Permission.query.filter(
        Permission.module == module,
        Permission.action == action,
    )
    if exclude_permission_id is not None:
        permission_query = permission_query.filter(
            Permission.permission_id != exclude_permission_id,
        )

    return permission_query.first()


def create_permission(
    *,
    module: str,
    action: str,
    description: str | None,
    is_active: bool,
) -> Permission:
    permission = Permission(
        module=module,
        action=action,
        description=description,
        is_active=is_active,
    )
    db.session.add(permission)
    return db_session_utils.commit_and_refresh(permission)


def update_permission(
    permission: Permission,
    *,
    module: str,
    action: str,
    description: str | None,
    is_active: bool,
) -> Permission:
    permission.module = module
    permission.action = action
    permission.description = description
    permission.is_active = is_active
    return db_session_utils.commit_and_refresh(permission)


def _apply_permission_filters(permission_query, filters: PermissionFilters | None):
    if not filters:
        return permission_query

    if filters.module:
        permission_query = permission_query.filter(Permission.module == filters.module)
    if filters.action:
        permission_query = permission_query.filter(Permission.action == filters.action)
    if filters.isActive is not None:
        permission_query = permission_query.filter(Permission.is_active == filters.isActive)

    return permission_query
