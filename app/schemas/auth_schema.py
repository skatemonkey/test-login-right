from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user_id: int
    username: str
    access_token: str
    permissions: list[str]


class ErrorResponse(BaseModel):
    error: str
