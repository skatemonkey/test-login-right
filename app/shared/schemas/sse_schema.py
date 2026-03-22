from pydantic import BaseModel


class SseConnectedPayload(BaseModel):
    message: str
