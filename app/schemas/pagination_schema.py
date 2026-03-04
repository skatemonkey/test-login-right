from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    page: int
    pageSize: int
    totalElements: int
    totalPages: int


class NotificationPagination(PaginatedResponse[T], Generic[T]):
    hasMore: bool
    # unreadCount: int
