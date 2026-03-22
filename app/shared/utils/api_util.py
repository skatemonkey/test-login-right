from typing import Any

from flask import Response, jsonify

NO_CONTENT_STATUSES = {204, 304}


def api_response(payload: Any, status: int):
    if status in NO_CONTENT_STATUSES or payload is None:
        return Response(status=status)

    if hasattr(payload, "model_dump"):
        payload = payload.model_dump()

    return jsonify(payload), status
