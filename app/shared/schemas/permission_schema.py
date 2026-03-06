from pydantic import BaseModel, Field

from app.shared.schemas.pagination_schema import TableQueryBase


class PermissionFilters(BaseModel):
    module: str | None = None
    action: str | None = None
    isActive: bool | None = None


class PermissionListQuery(TableQueryBase):
    filters: PermissionFilters | None = None


class PermissionItem(BaseModel):
    permissionId: int
    module: str
    action: str
    description: str | None = None
    isActive: bool
    createdAt: str
    updatedAt: str


class PermissionCreateRequest(BaseModel):
    module: str = Field(min_length=1, max_length=50)
    action: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=100)
    isActive: bool = True


class PermissionUpdateRequest(BaseModel):
    module: str = Field(min_length=1, max_length=50)
    action: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=100)
    isActive: bool = True
