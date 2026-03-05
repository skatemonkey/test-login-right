from typing import Generic, List, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class TableQueryBase(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1)
    sort_field: str | None = None
    sort_order: Literal["asc", "desc"] | None = None
    search: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    page: int
    page_size: int
    total_elements: int
    total_pages: int


class NotificationPagination(PaginatedResponse[T], Generic[T]):
    has_more: bool
    # unread_count: int
