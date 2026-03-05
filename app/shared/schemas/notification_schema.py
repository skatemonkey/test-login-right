from pydantic import BaseModel, Field


class MockApproveRequest(BaseModel):
    target_user_id: int
    item_id: int | None = None


class NotificationListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1)


class NotificationItem(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: str
