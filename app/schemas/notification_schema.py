from pydantic import BaseModel


class MockApproveRequest(BaseModel):
    targetUserId: int
    itemId: int | None = None


class NotificationItem(BaseModel):
    id: int
    userId: int
    message: str
    isRead: bool
    createdAt: str
