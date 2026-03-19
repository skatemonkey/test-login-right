from typing import Any

from app.module.notification import notification_repository, notification_stream
from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.schemas.notification_schema import NotificationItem
from app.shared.schemas.pagination_schema import NotificationPagination
from app.shared.utils import time as time_utils


def create_notification(user_id: int, message: str) -> tuple[dict[str, Any], int]:
    notification = notification_repository.create_notification(user_id, message)
    payload = _to_notification_payload(notification)
    print(
        f"[NOTI][create] notification_id={notification.id} user_id={user_id} message={message}",
        flush=True,
    )
    notification_stream.notification_hub.publish(user_id, {"type": "notification.created", "notification": payload})

    return {"message": "Notification sent", "notification": payload}, 201


def list_notifications_paginated(
    user_id: int,
    page: int,
    page_size: int,
) -> tuple[NotificationPagination[NotificationItem], int]:
    notifications, total_elements, total_pages = notification_repository.list_notifications_paginated(
        user_id=user_id,
        page=page,
        page_size=page_size,
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
    unread_count = notification_repository.get_unread_count(user_id)
    return {"userId": user_id, "unreadCount": unread_count}, 200


def mark_as_read(notification_id: int, user_id: int) -> tuple[dict[str, Any] | ErrorResponse, int]:
    notification = notification_repository.mark_notification_as_read(notification_id, user_id)
    if not notification:
        return ErrorResponse(error="Notification not found"), 404

    return {
        "message": "Notification marked as read",
        "notification": _to_notification_payload(notification),
    }, 200


def mark_all_as_read(user_id: int) -> tuple[dict[str, Any], int]:
    updated_count = notification_repository.mark_all_as_read(user_id)
    return {"message": "All notifications marked as read", "updatedCount": updated_count}, 200


def _to_notification_payload(notification) -> dict[str, Any]:
    return {
        "id": notification.id,
        "userId": notification.user_id,
        "message": notification.message,
        "isRead": bool(notification.is_read),
        "createdAt": time_utils.format_datetime(notification.created_at),
    }
