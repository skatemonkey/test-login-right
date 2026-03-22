from collections.abc import Generator
from queue import Empty

from flask import Blueprint, Response, stream_with_context
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.notification import notification_service, notification_stream
from app.shared.schemas.notification_schema import (
    MockApproveRequest,
    MockApproveResponse,
    NotificationListQuery,
    NotificationSseEvent,
)
from app.shared.schemas.sse_schema import SseConnectedPayload
from app.shared.utils import api_util, auth as auth_utils
from app.shared.utils.sse_util import to_sse

notification_bp = Blueprint("notification", __name__)

@notification_bp.get("")
@jwt_required()
@validate()
def get_my_notifications(query: NotificationListQuery):
    result, status = notification_service.list_notifications_paginated(
        user_id=auth_utils.current_user_id(),
        page=query.page,
        page_size=query.pageSize,
    )
    return api_util.model_response(result, status)


@notification_bp.patch("/<int:notification_id>/read")
@jwt_required()
@validate()
def mark_notification_as_read(notification_id: int):
    result, status = notification_service.mark_as_read(notification_id, auth_utils.current_user_id())
    return api_util.model_response(result, status)


@notification_bp.patch("/read-all")
@jwt_required()
@validate()
def mark_all_notifications_as_read():
    result, status = notification_service.mark_all_as_read(auth_utils.current_user_id())
    return api_util.model_response(result, status)


@notification_bp.get("/unread-count")
@jwt_required()
@validate()
def get_unread_count():
    result, status = notification_service.get_unread_count(auth_utils.current_user_id())
    return api_util.model_response(result, status)


@notification_bp.get("/stream")
@jwt_required()
@validate()
def stream_notifications():
    user_id = auth_utils.current_user_id()

    connection_id, event_queue = notification_stream.notification_hub.subscribe(user_id)
    print(
        f"[SSE][stream-open] user_id={user_id} connection_id={connection_id}",
        flush=True,
    )

    @stream_with_context
    def event_stream() -> Generator[str, None, None]:
        try:
            yield to_sse(
                event="connected",
                data=SseConnectedPayload(message="connected"),
            )
            while True:
                try:
                    payload = event_queue.get(timeout=20)
                    print(
                        f"[SSE][send] user_id={user_id} connection_id={connection_id} payload={payload}",
                        flush=True,
                    )
                    yield to_sse(
                        event="notification",
                        data=NotificationSseEvent.model_validate(payload),
                    )
                except Empty:
                    print(
                        f"[SSE][ping] user_id={user_id} connection_id={connection_id}",
                        flush=True,
                    )
                    yield ": ping\n\n"
        finally:
            notification_stream.notification_hub.unsubscribe(user_id, connection_id)
            print(
                f"[SSE][stream-close] user_id={user_id} connection_id={connection_id}",
                flush=True,
            )

    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@notification_bp.post("/mock-approve")
@jwt_required()
@validate()
def mock_approve(body: MockApproveRequest):
    approver_user_id = auth_utils.current_user_id()

    item_label = body.itemId if body.itemId is not None else "N/A"
    message = f"Item {item_label} was approved by user {approver_user_id}."
    created, status = notification_service.create_notification(
        user_id=body.targetUserId,
        message=message,
    )

    return api_util.model_response(
        MockApproveResponse(
            message="Approve action mocked and notification sent",
            approverUserId=approver_user_id,
            targetUserId=body.targetUserId,
            itemId=body.itemId,
            notification=created["notification"],
        ),
        status,
    )
