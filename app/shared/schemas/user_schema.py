from pydantic import BaseModel, Field, RootModel

from app.shared.schemas.pagination_schema import TableQueryBase


class UserFilters(BaseModel):
    isActive: bool | None = None


class UserListQuery(TableQueryBase):
    filters: UserFilters | None = None


class UserListItem(BaseModel):
    userId: int
    username: str
    email: str
    isActive: bool
    permissionCount: int
    createdAt: str
    updatedAt: str


class UserDetail(BaseModel):
    userId: int
    username: str
    email: str
    isActive: bool
    permissionIds: list[int]
    createdAt: str
    updatedAt: str


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)
    isActive: bool = True


class UserUpdateRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=3, max_length=100)
    password: str | None = Field(default=None, max_length=255)
    isActive: bool = True


class UserOptionItem(BaseModel):
    userId: int
    username: str


class UserPermissionToggleRequest(BaseModel):
    enabled: bool


class PermissionMatrixItem(BaseModel):
    permissionId: int
    module: str
    action: str


class PermissionMatrixResponse(RootModel[list[PermissionMatrixItem]]):
    pass


class UserOptionsResponse(RootModel[list[UserOptionItem]]):
    pass


class UserPermissionToggleResult(BaseModel):
    userId: int
    permissionId: int
    enabled: bool
