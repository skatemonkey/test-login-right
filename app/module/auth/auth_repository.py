from sqlalchemy.orm import selectinload

from app.shared.model.user import User
from app.shared.model.user_permission import UserPermission


def get_user_by_username(username: str):
    return (
        User.query
        .options(
            selectinload(User.permissions).selectinload(UserPermission.permission),
        )
        .filter_by(username=username)
        .first()
    )
