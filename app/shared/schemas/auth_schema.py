from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    userId: int
    username: str
    accessToken: str
    permissions: list[str]
