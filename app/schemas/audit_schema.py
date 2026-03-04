from pydantic import BaseModel
from typing import Optional, Union, List, Any


class AuditLogRequest(BaseModel):
    userId: int
    module: str
    action: str
    device: str
    details: Optional[Union[str, dict]] = None


class AuditLogFilters(BaseModel):
    module: Optional[str] = None
    action: Optional[str] = None
    dateFrom: Optional[str] = None
    dateTo: Optional[str] = None


class TableQuery(BaseModel):
    page: int
    pageSize: int
    sortField: Optional[str] = None
    sortOrder: Optional[str] = None
    search: Optional[str] = None
    filters: Optional[AuditLogFilters] = None


class AuditLogItem(BaseModel):
    id: int
    username: str
    ip: str
    device: str
    createdAt: str
    module: str
    action: str
    details: str


class PaginatedAuditLogResponse(BaseModel):
    data: List[AuditLogItem]
    page: int
    pageSize: int
    totalElements: int
    totalPages: int