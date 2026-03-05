from pydantic import BaseModel, Field
from app.shared.schemas.pagination_schema import TableQueryBase


class PermissionFilters(BaseModel):
    module: str | None = None
    action: str | None = None
    is_active: bool | None = None


class PermissionListQuery(TableQueryBase):
    filters: PermissionFilters | None = None


class PermissionItem(BaseModel):
    permission_id: int
    module: str
    action: str
    description: str | None = None
    is_active: bool
    created_at: str
    updated_at: str


class PermissionCreateRequest(BaseModel):
    module: str = Field(min_length=1, max_length=50)
    action: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=100)
    is_active: bool = True


class PermissionUpdateRequest(BaseModel):
    module: str = Field(min_length=1, max_length=50)
    action: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=100)
    is_active: bool = True
