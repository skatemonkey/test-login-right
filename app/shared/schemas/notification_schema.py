from pydantic import BaseModel, Field


class MockApproveRequest(BaseModel):
    targetUserId: int
    itemId: int | None = None


class NotificationListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1)


class NotificationItem(BaseModel):
    id: int
    userId: int
    message: str
    isRead: bool
    createdAt: str
