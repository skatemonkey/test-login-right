from pydantic import BaseModel, Field

from app.shared.schemas.pagination_schema import TableQueryBase


class UserFilters(BaseModel):
    is_active: bool | None = None


class UserListQuery(TableQueryBase):
    filters: UserFilters | None = None


class UserListItem(BaseModel):
    user_id: int
    username: str
    email: str
    is_active: bool
    permission_count: int
    created_at: str
    updated_at: str


class UserDetail(BaseModel):
    user_id: int
    username: str
    email: str
    is_active: bool
    permission_ids: list[int]
    created_at: str
    updated_at: str


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=3, max_length=100)
    password: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class UserPermissionToggleRequest(BaseModel):
    enabled: bool


class PermissionMatrixItem(BaseModel):
    permission_id: int
    module: str
    action: str
