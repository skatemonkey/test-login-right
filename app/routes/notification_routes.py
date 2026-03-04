import json
from collections.abc import Generator
from queue import Empty

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_pydantic import validate

from ..models.user import User
from ..schemas.notification_schema import MockApproveRequest
from ..services import notification_service
from ..services.notification_stream import notification_hub

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("", methods=["GET"])
@jwt_required()
def get_my_notifications():
    user_id = _resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    page, page_size, error = _parse_pagination_query()
    if error:
        return jsonify(error), 400

    result, status = notification_service.list_notifications_paginated(
        user_id=user_id,
        page=page,
        page_size=page_size,
    )
    return jsonify(result.model_dump()), status


@notification_bp.route("/<int:notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_notification_as_read(notification_id: int):
    user_id = _resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    result, status = notification_service.mark_as_read(notification_id, user_id)
    return jsonify(result), status


@notification_bp.route("/read-all", methods=["PATCH"])
@jwt_required()
def mark_all_notifications_as_read():
    user_id = _resolve_current_user_id()
    if user_id is None:
        return jsonify({"error": "Invalid access token"}), 401

    result, status = notification_service.mark_all_as_read(user_id)
    return jsonify(result), status


@notification_bp.route("/stream", methods=["GET"])
@jwt_required()
def stream_notifications():
    user_id = _resolve_current_user_id()
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


@notification_bp.route("/mock-approve", methods=["POST"])
@jwt_required()
@validate()
def mock_approve(body: MockApproveRequest):
    approver_user_id = _resolve_current_user_id()
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


def _resolve_current_user_id() -> int | None:
    claims = get_jwt()
    user_id = claims.get("user_id")
    if user_id is not None:
        return int(user_id)

    username = get_jwt_identity()
    if not username:
        return None

    user = User.query.filter_by(username=username).first()
    return user.user_id if user else None
    return user_id

def _to_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _parse_pagination_query() -> tuple[int, int, dict | None]:
    raw_page = request.args.get("page", "1")
    raw_page_size = request.args.get("pageSize", "10")

    try:
        page = int(raw_page)
        page_size = int(raw_page_size)
    except ValueError:
        return 1, 10, {"error": "page and pageSize must be integers"}

    if page < 1:
        return 1, 10, {"error": "page must be >= 1"}
    if page_size < 1:
        return 1, 10, {"error": "pageSize must be >= 1"}

    return page, page_size, None
