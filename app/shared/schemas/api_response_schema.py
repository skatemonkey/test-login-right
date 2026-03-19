from typing import Any

from pydantic import BaseModel, model_serializer


class ErrorResponse(BaseModel):
    error: str
    details: str | dict[str, Any] | None = None

    @model_serializer(mode="plain")
    def serialize(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"error": self.error}
        if self.details is not None:
            payload["details"] = self.details
        return payload
