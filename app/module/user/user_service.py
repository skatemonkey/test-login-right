import json

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.module.audit import audit_service
from app.module.user import user_repository
from app.shared.schemas.api_response_schema import ErrorResponse, MsgCodeDataResponse
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.schemas.user_schema import (
    PermissionMatrixItem,
    PermissionMatrixResponse,
    UserCreateRequest,
    UserDetail,
    UserListItem,
    UserListQuery,
    UserPermissionToggleResult,
    UserUpdateRequest,
)
from app.shared.utils import auth as auth_utils, time as time_utils

ALLOWED_PERMISSION_ACTIONS = ("view", "create", "update", "delete", "approve")
ACTION_ORDER = {action: idx for idx, action in enumerate(ALLOWED_PERMISSION_ACTIONS)}


def query_users(query: UserListQuery):
    users, total, total_pages = user_repository.query_users(query)

    permission_count_map = user_repository.get_permission_count_map([user.user_id for user in users])
    data = [
        UserListItem(
            userId=user.user_id,
            username=user.username or "",
            email=user.email or "",
            isActive=bool(user.is_active),
            permissionCount=permission_count_map.get(user.user_id, 0),
            createdAt=time_utils.format_datetime(user.created_at),
            updatedAt=time_utils.format_datetime(user.updated_at),
        )
        for user in users
    ]

    return PaginatedResponse[UserListItem](
        data=data,
        page=query.page,
        pageSize=query.pageSize,
        totalElements=total,
        totalPages=total_pages,
    ), 200


def get_user_detail(user_id: int):
    user = user_repository.get_user_by_id(user_id, with_permissions=True)
    if not user:
        return ErrorResponse(error="User not found"), 404
    return _map_user_detail(user), 200


def create_user(req: UserCreateRequest):
    username = req.username
    email = req.email
    password = req.password

    if not username or not email or not password:
        return ErrorResponse(error="Username, email, and password are required"), 400
    if len(password) < 8:
        return ErrorResponse(error="Password must be at least 8 characters"), 400

    if user_repository.username_exists(username):
        return ErrorResponse(error="Username already exists"), 409

    try:
        user = user_repository.create_user(
            username=username,
            email=email,
            password_hash=_hash_password(password),
            is_active=req.isActive,
        )
    except IntegrityError as exc:
        if _is_duplicate_username_error(exc):
            return ErrorResponse(error="Username already exists"), 409
        return ErrorResponse(error="Failed to create user"), 500

    user_detail = _map_user_detail(user)

    audit_service.create_log_internal(
        user_id=auth_utils.current_user_id(),
        module="user",
        action="create",
        details=f"user {user.username or ''} created: {user_detail.model_dump_json()}",
    )

    return MsgCodeDataResponse[UserDetail](
        msgCode="user.created",
        data=user_detail,
    ), 201


def update_user(user_id: int, req: UserUpdateRequest):
    user = user_repository.get_user_by_id(user_id, with_permissions=True)
    if not user:
        return ErrorResponse(error="User not found"), 404

    original_user = _map_user_detail(user).model_dump_json()

    username = req.username
    email = req.email
    password = req.password or ""

    if not username or not email:
        return ErrorResponse(error="Username and email are required"), 400
    if password and len(password) < 8:
        return ErrorResponse(error="Password must be at least 8 characters"), 400

    if user_repository.username_exists(username, exclude_user_id=user_id):
        return ErrorResponse(error="Username already exists"), 409

    try:
        user = user_repository.update_user(
            user,
            username=username,
            email=email,
            is_active=req.isActive,
            password_hash=_hash_password(password) if password else None,
        )
    except IntegrityError as exc:
        if _is_duplicate_username_error(exc):
            return ErrorResponse(error="Username already exists"), 409
        return ErrorResponse(error="Failed to update user"), 500

    updated_user_detail = _map_user_detail(user)

    audit_service.create_log_internal(
        user_id=auth_utils.current_user_id(),
        module="user",
        action="update",
        details=(
            f"user {user.user_id} updated: "
            f"[Original Data: {original_user}] "
            f"[Updated Data:{updated_user_detail.model_dump_json()}]"
        ),
    )

    return MsgCodeDataResponse[UserDetail](
        msgCode="user.updated",
        data=updated_user_detail,
    ), 200


def get_permission_matrix():
    permissions = user_repository.get_active_permissions(ALLOWED_PERMISSION_ACTIONS)

    sorted_permissions = sorted(
        permissions,
        key=lambda permission: (
            permission.module or "",
            ACTION_ORDER.get((permission.action or "").lower(), len(ACTION_ORDER)),
            permission.permission_id,
        ),
    )

    return PermissionMatrixResponse([
        PermissionMatrixItem(
            permissionId=permission.permission_id,
            module=permission.module or "",
            action=(permission.action or "").lower(),
        )
        for permission in sorted_permissions
    ]), 200


def toggle_user_permission(user_id: int, permission_id: int, enabled: bool):
    user = user_repository.get_user_by_id(user_id)
    if not user:
        return ErrorResponse(error="User not found"), 404

    permission = user_repository.get_permission_by_id(permission_id)
    if not permission:
        return ErrorResponse(error="Permission not found"), 404

    permission_action = (permission.action or "").lower()
    if not permission.is_active or permission_action not in ACTION_ORDER:
        return ErrorResponse(error="Permission is not assignable"), 400

    try:
        user_repository.set_user_permission(user_id, permission_id, enabled)
    except IntegrityError:
        return ErrorResponse(error="Failed to update user permission"), 500

    audit_service.create_log_internal(
        user_id=auth_utils.current_user_id(),
        module="user",
        action="update",
        details=f"user {user_id} permission updated: {json.dumps({
            'userId': user_id,
            'permissionId': permission_id,
            'module': permission.module or '',
            'action': permission_action,
            'enabled': enabled,
        })}",
    )

    return MsgCodeDataResponse[UserPermissionToggleResult](
        msgCode="user.permission.updated",
        data=UserPermissionToggleResult(
            userId=user_id,
            permissionId=permission_id,
            enabled=enabled,
        ),
    ), 200


def _map_user_detail(user) -> UserDetail:
    permission_ids = sorted(
        {
            user_permission.permission_id
            for user_permission in user.permissions
        },
    )
    return UserDetail(
        userId=user.user_id,
        username=user.username or "",
        email=user.email or "",
        isActive=bool(user.is_active),
        permissionIds=permission_ids,
        createdAt=time_utils.format_datetime(user.created_at),
        updatedAt=time_utils.format_datetime(user.updated_at),
    )


def _is_duplicate_username_error(exc: IntegrityError) -> bool:
    return "username" in str(getattr(exc, "orig", exc)).lower()


def _hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)
