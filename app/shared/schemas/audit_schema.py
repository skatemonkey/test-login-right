from typing import Optional, Union

from pydantic import BaseModel
from app.shared.schemas.pagination_schema import TableQueryBase


class AuditLogRequest(BaseModel):
    user_id: int
    module: str
    action: str
    device: str
    details: Optional[Union[str, dict]] = None


class AuditLogFilters(BaseModel):
    module: Optional[str] = None
    action: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class AuditLogQuery(TableQueryBase):
    filters: Optional[AuditLogFilters] = None


class AuditLogItem(BaseModel):
    id: int
    username: str | None = None
    ip: str
    device: str
    created_at: str
    module: str
    action: str
    details: str
