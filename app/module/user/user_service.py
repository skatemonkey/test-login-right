from collections.abc import Iterable

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.core import db
from app.shared.repository.permission import Permission
from app.shared.repository.user import User
from app.shared.repository.user_permission import UserPermission
from app.shared.schemas.pagination_schema import PaginatedResponse
from app.shared.schemas.user_schema import (
    PermissionMatrixItem,
    UserCreateRequest,
    UserDetail,
    UserListItem,
    UserListQuery,
    UserUpdateRequest,
)
from app.shared.utils import pagination_utils

ALLOWED_PERMISSION_ACTIONS = ("view", "create", "update", "delete", "approve")
ACTION_ORDER = {action: idx for idx, action in enumerate(ALLOWED_PERMISSION_ACTIONS)}


def query_users(query: UserListQuery):
    q = User.query

    # Search
    q = pagination_utils.apply_search(q, query.search, [User.username, User.email])

    # Filters
    q = _apply_user_filters(q, query)

    # Sort
    field_map = {
        "user_id": User.user_id,
        "username": User.username,
        "email": User.email,
        "is_active": User.is_active,
        "created_at": User.created_at,
        "updated_at": User.updated_at,
    }
    q = pagination_utils.apply_sorting(
        q,
        query.sort_field or "updated_at",
        query.sort_order or "desc",
        field_map,
        User.updated_at,
    )

    # Paginate
    users, total, total_pages = pagination_utils.paginate(q, query.page, query.page_size)

    # Map
    permission_count_map = _get_permission_count_map([user.user_id for user in users])
    data = [
        UserListItem(
            user_id=user.user_id,
            username=user.username or "",
            email=user.email or "",
            is_active=bool(user.is_active),
            permission_count=permission_count_map.get(user.user_id, 0),
            created_at=_format_datetime(user.created_at),
            updated_at=_format_datetime(user.updated_at),
        )
        for user in users
    ]

    return PaginatedResponse[UserListItem](
        data=data,
        page=query.page,
        page_size=query.page_size,
        total_elements=total,
        total_pages=total_pages,
    ), 200


def get_user_detail(user_id: int):
    user = User.query.filter_by(user_id=user_id).first()
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

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 409

    user = User(
        username=username,
        email=email,
        password_hash=_hash_password(password),
        is_active=req.is_active,
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        if _is_duplicate_username_error(exc):
            return {"error": "Username already exists"}, 409
        return {"error": "Failed to create user"}, 500

    return {
        "message": "User created",
        "data": _map_user_detail(user).model_dump(),
    }, 201


def update_user(user_id: int, req: UserUpdateRequest):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return {"error": "User not found"}, 404

    username = req.username
    email = req.email
    password = req.password or ""

    if not username or not email:
        return {"error": "Username and email are required"}, 400
    if password and len(password) < 8:
        return {"error": "Password must be at least 8 characters"}, 400

    duplicate = (
        User.query
        .filter(User.user_id != user_id, User.username == username)
        .first()
    )
    if duplicate:
        return {"error": "Username already exists"}, 409

    user.username = username
    user.email = email
    user.is_active = req.is_active
    if password:
        user.password_hash = _hash_password(password)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        if _is_duplicate_username_error(exc):
            return {"error": "Username already exists"}, 409
        return {"error": "Failed to update user"}, 500

    return {
        "message": "User updated",
        "data": _map_user_detail(user).model_dump(),
    }, 200


def get_permission_matrix():
    permissions = (
        Permission.query
        .filter(
            Permission.is_active.is_(True),
            Permission.action.in_(ALLOWED_PERMISSION_ACTIONS),
        )
        .all()
    )

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
            permission_id=permission.permission_id,
            module=permission.module or "",
            action=(permission.action or "").lower(),
        ).model_dump()
        for permission in sorted_permissions
    ]

    return {"data": data}, 200


def toggle_user_permission(user_id: int, permission_id: int, enabled: bool):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return {"error": "User not found"}, 404

    permission = Permission.query.filter_by(permission_id=permission_id).first()
    if not permission:
        return {"error": "Permission not found"}, 404

    action = (permission.action or "").lower()
    if not permission.is_active or action not in ACTION_ORDER:
        return {"error": "Permission is not assignable"}, 400

    link = UserPermission.query.filter_by(
        user_id=user_id,
        permission_id=permission_id,
    ).first()

    if enabled and not link:
        db.session.add(UserPermission(user_id=user_id, permission_id=permission_id))
    if not enabled and link:
        db.session.delete(link)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Failed to update user permission"}, 500

    return {
        "message": "User permission updated",
        "data": {
            "user_id": user_id,
            "permission_id": permission_id,
            "enabled": enabled,
        },
    }, 200


def _get_permission_count_map(user_ids: Iterable[int]) -> dict[int, int]:
    user_ids_list = list(user_ids)
    if not user_ids_list:
        return {}

    rows = (
        db.session.query(UserPermission.user_id, func.count(UserPermission.id))
        .filter(UserPermission.user_id.in_(user_ids_list))
        .group_by(UserPermission.user_id)
        .all()
    )
    return {int(user_id): int(count) for user_id, count in rows}


def _map_user_detail(user: User) -> UserDetail:
    permission_ids = sorted(
        {
            user_permission.permission_id
            for user_permission in user.permissions
        },
    )
    return UserDetail(
        user_id=user.user_id,
        username=user.username or "",
        email=user.email or "",
        is_active=bool(user.is_active),
        permission_ids=permission_ids,
        created_at=_format_datetime(user.created_at),
        updated_at=_format_datetime(user.updated_at),
    )


def _apply_user_filters(q, query: UserListQuery):
    if query.filters and query.filters.is_active is not None:
        q = q.filter(User.is_active == query.filters.is_active)
    return q


def _format_datetime(value) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else ""


def _is_duplicate_username_error(exc: IntegrityError) -> bool:
    return "username" in str(getattr(exc, "orig", exc)).lower()


def _hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)
