from sqlalchemy.exc import IntegrityError

from app.module.permission import permission_repository
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.schemas.permission_schema import (
    PermissionCreateRequest,
    PermissionItem,
    PermissionListQuery,
    PermissionUpdateRequest,
)


def get_permissions(query: PermissionListQuery):
    results, total, total_pages = permission_repository.get_permissions(query)

    # Map
    data = [map_permission(permission) for permission in results]

    return PaginatedResponse[PermissionItem](
        data=data,
        page=query.page,
        pageSize=query.pageSize,
        totalElements=total,
        totalPages=total_pages
    ), 200


def map_permission(permission):
    return PermissionItem(
        permissionId=permission.permission_id,
        module=permission.module or "",
        action=permission.action or "",
        description=permission.description,
        isActive=bool(permission.is_active),
        createdAt=permission.created_at.strftime("%Y-%m-%d %H:%M:%S") if permission.created_at else "",
        updatedAt=permission.updated_at.strftime("%Y-%m-%d %H:%M:%S") if permission.updated_at else "",
    )


def create_permission(body: PermissionCreateRequest):
    module = body.module
    action = body.action
    description = body.description

    if not module or not action:
        return {"error": "Module and action are required"}, 400

    if permission_repository.get_permission_by_module_and_action(module, action):
        return {"error": "Permission already exists"}, 409

    try:
        permission = permission_repository.create_permission(
            module=module,
            action=action,
            description=description,
            is_active=body.isActive,
        )
    except IntegrityError:
        return {"error": "Permission already exists"}, 409

    return {
        "message": "Permission created",
        "data": map_permission(permission).model_dump(),
    }, 201


def update_permission(permission_id: int, body: PermissionUpdateRequest):
    permission = permission_repository.get_permission_by_id(permission_id)
    if not permission:
        return {"error": "Permission not found"}, 404

    module = body.module
    action = body.action
    description = body.description

    if not module or not action:
        return {"error": "Module and action are required"}, 400

    duplicate = permission_repository.get_permission_by_module_and_action(
        module,
        action,
        exclude_permission_id=permission_id,
    )
    if duplicate:
        return {"error": "Permission already exists"}, 409

    try:
        permission = permission_repository.update_permission(
            permission,
            module=module,
            action=action,
            description=description,
            is_active=body.isActive,
        )
    except IntegrityError:
        return {"error": "Permission already exists"}, 409

    return {
        "message": "Permission updated",
        "data": map_permission(permission).model_dump(),
    }, 200
