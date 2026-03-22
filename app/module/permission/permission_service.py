from sqlalchemy.exc import IntegrityError

from app.module.permission import permission_repository
from app.shared.schemas.api_response_schema import ErrorResponse, MsgCodeDataResponse
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.schemas.permission_schema import (
    PermissionCreateRequest,
    PermissionItem,
    PermissionListQuery,
    PermissionUpdateRequest,
)
from app.shared.utils import time as time_utils


def get_permissions(query: PermissionListQuery):
    results, total, total_pages = permission_repository.get_permissions(query)

    data = [_map_permission(permission) for permission in results]

    return PaginatedResponse[PermissionItem](
        data=data,
        page=query.page,
        pageSize=query.pageSize,
        totalElements=total,
        totalPages=total_pages
    ), 200


def _map_permission(permission):
    return PermissionItem(
        permissionId=permission.permission_id,
        module=permission.module or "",
        action=permission.action or "",
        description=permission.description,
        isActive=bool(permission.is_active),
        createdAt=time_utils.format_datetime(permission.created_at),
        updatedAt=time_utils.format_datetime(permission.updated_at),
    )


def create_permission(body: PermissionCreateRequest):
    module = body.module
    action = body.action
    description = body.description

    if not module or not action:
        return ErrorResponse(error="Module and action are required"), 400

    if permission_repository.get_permission_by_module_and_action(module, action):
        return ErrorResponse(error="Permission already exists"), 409

    try:
        permission = permission_repository.create_permission(
            module=module,
            action=action,
            description=description,
            is_active=body.isActive,
        )
    except IntegrityError:
        return ErrorResponse(error="Permission already exists"), 409

    return MsgCodeDataResponse[PermissionItem](
        msgCode="permission.created",
        data=_map_permission(permission),
    ), 201


def update_permission(permission_id: int, body: PermissionUpdateRequest):
    permission = permission_repository.get_permission_by_id(permission_id)
    if not permission:
        return ErrorResponse(error="Permission not found"), 404

    module = body.module
    action = body.action
    description = body.description

    if not module or not action:
        return ErrorResponse(error="Module and action are required"), 400

    duplicate = permission_repository.get_permission_by_module_and_action(
        module,
        action,
        exclude_permission_id=permission_id,
    )
    if duplicate:
        return ErrorResponse(error="Permission already exists"), 409

    try:
        permission = permission_repository.update_permission(
            permission,
            module=module,
            action=action,
            description=description,
            is_active=body.isActive,
        )
    except IntegrityError:
        return ErrorResponse(error="Permission already exists"), 409

    return MsgCodeDataResponse[PermissionItem](
        msgCode="permission.updated",
        data=_map_permission(permission),
    ), 200
