from typing import Any, Generic, TypeVar

from pydantic import BaseModel, model_serializer

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: str
    details: str | dict[str, Any] | None = None

    @model_serializer(mode="plain")
    def serialize(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"error": self.error}
        if self.details is not None:
            payload["details"] = self.details
        return payload


class MsgCodeDataResponse(BaseModel, Generic[T]):
    msgCode: str
    data: T
