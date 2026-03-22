from typing import Any

from flask import Response, jsonify
from pydantic import BaseModel

NO_CONTENT_STATUSES = {204, 304}


# Use for routes whose non-empty payload is a Pydantic model.
def model_response(payload: BaseModel | None, status: int):
    if status in NO_CONTENT_STATUSES or payload is None:
        return Response(status=status)

    return jsonify(payload.model_dump()), status

# Use for routes whose payload is already plain JSON-ready data.
def json_response(payload: Any, status: int):
    return jsonify(payload), status
