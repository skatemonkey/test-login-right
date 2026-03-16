from sqlalchemy.exc import IntegrityError

from app.core import db
from app.shared.model.permission import Permission
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.schemas.permission_schema import (
    PermissionCreateRequest,
    PermissionFilters,
    PermissionItem,
    PermissionListQuery,
    PermissionUpdateRequest,
)
from app.shared.utils import pagination_utils


def get_permissions(query: PermissionListQuery):
    q = Permission.query

    # Search
    q = pagination_utils.apply_search(q, query.search, [
        Permission.module, Permission.action, Permission.description
    ])

    # Filters
    q = apply_permission_filters(q, query.filters)

    # Sort
    field_map = {
        'permissionId': Permission.permission_id,
        'module': Permission.module,
        'action': Permission.action,
        'description': Permission.description,
        'isActive': Permission.is_active,
        'createdAt': Permission.created_at,
        'updatedAt': Permission.updated_at
    }
    q = pagination_utils.apply_sorting(q, query.sortField or 'updatedAt', query.sortOrder or 'desc', field_map,
                                       Permission.updated_at)

    # Paginate
    results, total, total_pages = pagination_utils.paginate(q, query.page, query.pageSize)

    # Map
    data = [map_permission(permission) for permission in results]

    return PaginatedResponse[PermissionItem](
        data=data,
        page=query.page,
        pageSize=query.pageSize,
        totalElements=total,
        totalPages=total_pages
    ), 200


# ============================================================
# Helper functions for get_permissions
# ============================================================

def apply_permission_filters(q, filters: PermissionFilters | None):
    if not filters:
        return q
    if filters.module:
        q = q.filter(Permission.module == filters.module)
    if filters.action:
        q = q.filter(Permission.action == filters.action)
    if filters.isActive is not None:
        q = q.filter(Permission.is_active == filters.isActive)
    return q


def map_permission(permission):
    return PermissionItem(
        permissionId=permission.permission_id,
        module=permission.module or '',
        action=permission.action or '',
        description=permission.description,
        isActive=bool(permission.is_active),
        createdAt=permission.created_at.strftime('%Y-%m-%d %H:%M:%S') if permission.created_at else '',
        updatedAt=permission.updated_at.strftime('%Y-%m-%d %H:%M:%S') if permission.updated_at else ''
    )


def create_permission(body: PermissionCreateRequest):
    module = body.module
    action = body.action
    description = body.description

    if not module or not action:
        return {"error": "Module and action are required"}, 400

    if Permission.query.filter_by(module=module, action=action).first():
        return {"error": "Permission already exists"}, 409

    permission = Permission(
        module=module,
        action=action,
        description=description,
        is_active=body.isActive,
    )

    try:
        db.session.add(permission)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Permission already exists"}, 409

    return {
        "message": "Permission created",
        "data": map_permission(permission).model_dump(),
    }, 201


def update_permission(permission_id: int, body: PermissionUpdateRequest):
    permission = Permission.query.filter_by(permission_id=permission_id).first()
    if not permission:
        return {"error": "Permission not found"}, 404

    module = body.module
    action = body.action
    description = body.description

    if not module or not action:
        return {"error": "Module and action are required"}, 400

    duplicate = (
        Permission.query
        .filter(
            Permission.permission_id != permission_id,
            Permission.module == module,
            Permission.action == action,
        )
        .first()
    )
    if duplicate:
        return {"error": "Permission already exists"}, 409

    permission.module = module
    permission.action = action
    permission.description = description
    permission.is_active = body.isActive

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Permission already exists"}, 409

    return {
        "message": "Permission updated",
        "data": map_permission(permission).model_dump(),
    }, 200
