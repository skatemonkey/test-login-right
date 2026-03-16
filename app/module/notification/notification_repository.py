from sqlalchemy import update

from app.core import db
from app.shared.model.notification import Notification
from app.shared.utils import db_session_utils


def create_notification(user_id: int, message: str) -> Notification:
    notification = Notification(user_id=user_id, message=message, is_read=False)
    db.session.add(notification)
    return db_session_utils.commit_and_refresh(notification)


def list_notifications(user_id: int) -> list[Notification]:
    return (
        Notification.query
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def list_notifications_paginated(
    user_id: int,
    page: int,
    page_size: int,
) -> tuple[list[Notification], int, int]:
    notifications_query = (
        Notification.query
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    )

    total_elements = notifications_query.count()
    total_pages = (total_elements + page_size - 1) // page_size if page_size > 0 else 0
    offset = (page - 1) * page_size
    notifications = (
        notifications_query
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return notifications, total_elements, total_pages


def get_unread_count(user_id: int) -> int:
    return (
        Notification.query
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .count()
    )


def mark_notification_as_read(notification_id: int, user_id: int) -> Notification | None:
    notification = get_notification_for_user(notification_id, user_id)
    if not notification:
        return None

    if not notification.is_read:
        notification.is_read = True
        notification = db_session_utils.commit_and_refresh(notification)

    return notification


def mark_all_as_read(user_id: int) -> int:
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True)
    )
    result = db.session.execute(stmt)
    updated_count = int(result.rowcount or 0)

    if updated_count > 0:
        db_session_utils.commit_session()

    return updated_count


def get_notification_for_user(notification_id: int, user_id: int) -> Notification | None:
    return Notification.query.filter_by(id=notification_id, user_id=user_id).first()
