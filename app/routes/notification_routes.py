import json
from collections.abc import Generator
from queue import Empty

from flask import Blueprint, Response, jsonify, stream_with_context
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from ..schemas.notification_schema import MockApproveRequest, NotificationListQuery
from ..services import notification_service
from ..services.notification_stream import notification_hub
from ..utils.auth_utils import resolve_current_user_id

notification_bp = Blueprint("notification", __name__)


@notification_bp.get("")
@jwt_required()
@validate()
def get_my_notifications(query: NotificationListQuery):
    user_id = resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    result, status = notification_service.list_notifications_paginated(
        user_id=user_id,
        page=query.page,
        page_size=query.pageSize,
    )
    return jsonify(result.model_dump()), status


@notification_bp.patch("/<int:notification_id>/read")
@jwt_required()
@validate()
def mark_notification_as_read(notification_id: int):
    user_id = resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    result, status = notification_service.mark_as_read(notification_id, user_id)
    return jsonify(result), status


@notification_bp.patch("/read-all")
@jwt_required()
@validate()
def mark_all_notifications_as_read():
    user_id = resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    result, status = notification_service.mark_all_as_read(user_id)
    return jsonify(result), status


@notification_bp.get("/unread-count/<int:user_id>")
@jwt_required()
@validate()
def get_unread_count(user_id: int):
    current_user_id = resolve_current_user_id()
    if current_user_id is None:
        return jsonify({"error": "Invalid access token"}), 401
    if current_user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    result, status = notification_service.get_unread_count(user_id)
    return jsonify(result), status


@notification_bp.get("/stream")
@jwt_required()
@validate()
def stream_notifications():
    user_id = resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    connection_id, event_queue = notification_hub.subscribe(user_id)
    print(
        f"[SSE][stream-open] user_id={user_id} connection_id={connection_id}",
        flush=True,
    )

    @stream_with_context
    def event_stream() -> Generator[str, None, None]:
        try:
            yield _to_sse(event="connected", data={"message": "connected"})
            while True:
                try:
                    payload = event_queue.get(timeout=20)
                    print(
                        f"[SSE][send] user_id={user_id} connection_id={connection_id} payload={payload}",
                        flush=True,
                    )
                    yield _to_sse(event="notification", data=payload)
                except Empty:
                    print(
                        f"[SSE][ping] user_id={user_id} connection_id={connection_id}",
                        flush=True,
                    )
                    yield ": ping\n\n"
        finally:
            notification_hub.unsubscribe(user_id, connection_id)
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
    approver_user_id = resolve_current_user_id()
    if approver_user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    item_label = body.itemId if body.itemId is not None else "N/A"
    message = f"Item {item_label} was approved by user {approver_user_id}."
    created, status = notification_service.create_notification(
        user_id=body.targetUserId,
        message=message,
    )

    return jsonify({
        "message": "Approve action mocked and notification sent",
        "approverUserId": approver_user_id,
        "targetUserId": body.targetUserId,
        "itemId": body.itemId,
        "notification": created["notification"],
    }), status

def _to_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
