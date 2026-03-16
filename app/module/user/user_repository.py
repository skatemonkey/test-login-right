from collections.abc import Iterable

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.core import db
from app.shared.model.permission import Permission
from app.shared.model.user import User
from app.shared.model.user_permission import UserPermission
from app.shared.schemas.user_schema import UserListQuery
from app.shared.utils import db_session_utils, pagination_utils


def query_users(query: UserListQuery):
    user_query = User.query
    user_query = pagination_utils.apply_search(
        user_query,
        query.search,
        [User.username, User.email],
    )
    user_query = _apply_user_filters(user_query, query)

    field_map = {
        "userId": User.user_id,
        "username": User.username,
        "email": User.email,
        "isActive": User.is_active,
        "createdAt": User.created_at,
        "updatedAt": User.updated_at,
    }
    user_query = pagination_utils.apply_sorting(
        user_query,
        query.sortField or "updatedAt",
        query.sortOrder or "desc",
        field_map,
        User.updated_at,
    )

    return pagination_utils.paginate(user_query, query.page, query.pageSize)


def get_permission_count_map(user_ids: Iterable[int]) -> dict[int, int]:
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


def get_user_by_id(user_id: int, *, with_permissions: bool = False) -> User | None:
    user_query = User.query
    if with_permissions:
        user_query = user_query.options(selectinload(User.permissions))

    return user_query.filter_by(user_id=user_id).first()


def username_exists(username: str, *, exclude_user_id: int | None = None) -> bool:
    user_query = User.query.filter(User.username == username)
    if exclude_user_id is not None:
        user_query = user_query.filter(User.user_id != exclude_user_id)
    return user_query.first() is not None


def create_user(
    *,
    username: str,
    email: str,
    password_hash: str,
    is_active: bool,
) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=is_active,
    )
    db.session.add(user)
    db_session_utils.commit_session()
    return get_user_by_id(user.user_id, with_permissions=True)


def update_user(
    user: User,
    *,
    username: str,
    email: str,
    is_active: bool,
    password_hash: str | None = None,
) -> User:
    user.username = username
    user.email = email
    user.is_active = is_active
    if password_hash:
        user.password_hash = password_hash

    db_session_utils.commit_session()
    return get_user_by_id(user.user_id, with_permissions=True)


def get_active_permissions(actions: Iterable[str]) -> list[Permission]:
    return (
        Permission.query
        .filter(
            Permission.is_active.is_(True),
            Permission.action.in_(list(actions)),
        )
        .all()
    )


def get_permission_by_id(permission_id: int) -> Permission | None:
    return Permission.query.filter_by(permission_id=permission_id).first()


def set_user_permission(user_id: int, permission_id: int, enabled: bool) -> None:
    link = UserPermission.query.filter_by(
        user_id=user_id,
        permission_id=permission_id,
    ).first()

    if enabled and not link:
        db.session.add(UserPermission(user_id=user_id, permission_id=permission_id))
    if not enabled and link:
        db.session.delete(link)

    db_session_utils.commit_session()


def _apply_user_filters(user_query, query: UserListQuery):
    if query.filters and query.filters.isActive is not None:
        user_query = user_query.filter(User.is_active == query.filters.isActive)
    return user_query
