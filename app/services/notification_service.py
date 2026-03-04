from typing import Any

from .. import db
from ..models.notification import Notification
from .notification_stream import notification_hub


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
    notifications = (
        Notification.query
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return {"data": [_to_notification_payload(item) for item in notifications]}, 200


def mark_as_read(notification_id: int, user_id: int) -> tuple[dict[str, Any], int]:
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        return {"error": "Notification not found"}, 404

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return {"message": "Notification marked as read"}, 200


def mark_all_as_read(user_id: int) -> tuple[dict[str, Any], int]:
    unread_notifications = (
        Notification.query
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .all()
    )

    for notification in unread_notifications:
        notification.is_read = True

    if unread_notifications:
        db.session.commit()

    return {"message": "All notifications marked as read", "updatedCount": len(unread_notifications)}, 200


def _to_notification_payload(notification: Notification) -> dict[str, Any]:
    return {
        "id": notification.id,
        "userId": notification.user_id,
        "message": notification.message,
        "isRead": bool(notification.is_read),
        "createdAt": notification.created_at.strftime("%Y-%m-%d %H:%M:%S") if notification.created_at else "",
    }
