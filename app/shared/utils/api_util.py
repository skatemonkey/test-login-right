from typing import Any

from flask import jsonify


def json_response(payload: Any, status: int):
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump()
    return jsonify(payload), status
