from typing import Any

from sqlalchemy import update

from app.core import db
from app.shared.repository import Notification
from app.shared.schemas.notification_schema import NotificationItem
from app.shared.schemas.pagination_schema import NotificationPagination
from app.module.notification.notification_stream import notification_hub


def create_notification(user_id: int, message: str) -> tuple[dict[str, Any], int]:
    notification = Notification(user_id=user_id, message=message, is_read=False)
    db.session.add(notification)
    db.session.commit()

    payload = _to_notification_payload(notification)
    print(
        f"[NOTI][create] notification_id={notification.id} user_id={user_id} message={message}",
        flush=True,
    )
    notification_hub.publish(user_id, {"type": "notification.created", "notification": payload})

    return {"message": "Notification sent", "notification": payload}, 201


def list_notifications(user_id: int) -> tuple[dict[str, Any], int]:
    notifications_query = (
        Notification.query
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )

    notifications = notifications_query.all()
    return {"data": [_to_notification_payload(item) for item in notifications]}, 200


def list_notifications_paginated(
    user_id: int,
    page: int,
    page_size: int,
) -> tuple[NotificationPagination[NotificationItem], int]:
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

    return NotificationPagination[NotificationItem](
        data=[_to_notification_payload(item) for item in notifications],
        page=page,
        pageSize=page_size,
        totalElements=total_elements,
        totalPages=total_pages,
        hasMore=page < total_pages,
    ), 200


def get_unread_count(user_id: int) -> tuple[dict[str, int], int]:
    unread_count = (
        Notification.query
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .count()
    )

    return {"userId": user_id, "unreadCount": unread_count}, 200


def mark_as_read(notification_id: int, user_id: int) -> tuple[dict[str, Any], int]:
    notification: Notification | None = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id,
    ).first()
    if not notification:
        return {"error": "Notification not found"}, 404

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return {
        "message": "Notification marked as read",
        "notification": _to_notification_payload(notification),
    }, 200


def mark_all_as_read(user_id: int) -> tuple[dict[str, Any], int]:
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
        db.session.commit()

    return {"message": "All notifications marked as read", "updatedCount": updated_count}, 200


def _to_notification_payload(notification: Notification) -> dict[str, Any]:
    return {
        "id": notification.id,
        "userId": notification.user_id,
        "message": notification.message,
        "isRead": bool(notification.is_read),
        "createdAt": notification.created_at.strftime("%Y-%m-%d %H:%M:%S") if notification.created_at else "",
    }
