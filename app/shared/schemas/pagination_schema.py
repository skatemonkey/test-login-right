from typing import Generic, List, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class TableQueryBase(BaseModel):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1)
    sortField: str | None = None
    sortOrder: Literal["asc", "desc"] | None = None
    search: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    page: int
    pageSize: int
    totalElements: int
    totalPages: int


class NotificationPagination(PaginatedResponse[T], Generic[T]):
    hasMore: bool
    # unreadCount: int
