import json

from pydantic import BaseModel


def to_sse(event: str, data: BaseModel) -> str:
    return f"event: {event}\ndata: {json.dumps(data.model_dump())}\n\n"
