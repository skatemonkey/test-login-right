from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.module.user import user_repository
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.schemas.user_schema import (
    PermissionMatrixItem,
    UserCreateRequest,
    UserDetail,
    UserListItem,
    UserListQuery,
    UserUpdateRequest,
)
from app.shared.utils import time as time_utils

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
        return {"error": "User not found"}, 404
    return _map_user_detail(user), 200


def create_user(req: UserCreateRequest):
    username = req.username
    email = req.email
    password = req.password

    if not username or not email or not password:
        return {"error": "Username, email, and password are required"}, 400
    if len(password) < 8:
        return {"error": "Password must be at least 8 characters"}, 400

    if user_repository.username_exists(username):
        return {"error": "Username already exists"}, 409

    try:
        user = user_repository.create_user(
            username=username,
            email=email,
            password_hash=_hash_password(password),
            is_active=req.isActive,
        )
    except IntegrityError as exc:
        if _is_duplicate_username_error(exc):
            return {"error": "Username already exists"}, 409
        return {"error": "Failed to create user"}, 500

    return {
        "message": "User created",
        "data": _map_user_detail(user).model_dump(),
    }, 201


def update_user(user_id: int, req: UserUpdateRequest):
    user = user_repository.get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}, 404

    username = req.username
    email = req.email
    password = req.password or ""

    if not username or not email:
        return {"error": "Username and email are required"}, 400
    if password and len(password) < 8:
        return {"error": "Password must be at least 8 characters"}, 400

    if user_repository.username_exists(username, exclude_user_id=user_id):
        return {"error": "Username already exists"}, 409

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
            return {"error": "Username already exists"}, 409
        return {"error": "Failed to update user"}, 500

    return {
        "message": "User updated",
        "data": _map_user_detail(user).model_dump(),
    }, 200


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

    data = [
        PermissionMatrixItem(
            permissionId=permission.permission_id,
            module=permission.module or "",
            action=(permission.action or "").lower(),
        ).model_dump()
        for permission in sorted_permissions
    ]

    return {"data": data}, 200


def toggle_user_permission(user_id: int, permission_id: int, enabled: bool):
    user = user_repository.get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}, 404

    permission = user_repository.get_permission_by_id(permission_id)
    if not permission:
        return {"error": "Permission not found"}, 404

    action = (permission.action or "").lower()
    if not permission.is_active or action not in ACTION_ORDER:
        return {"error": "Permission is not assignable"}, 400

    try:
        user_repository.set_user_permission(user_id, permission_id, enabled)
    except IntegrityError:
        return {"error": "Failed to update user permission"}, 500

    return {
        "message": "User permission updated",
        "data": {
            "userId": user_id,
            "permissionId": permission_id,
            "enabled": enabled,
        },
    }, 200


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
