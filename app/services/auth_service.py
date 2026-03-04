from flask_jwt_extended import create_access_token
from ..models.user import User
from ..schemas.auth_schema import LoginRequest, LoginResponse, ErrorResponse


def login(req: LoginRequest):
    user = User.query.filter_by(username=req.username).first()
    if not user or user.password_hash != req.password:
        return ErrorResponse(error="Invalid credentials"), 401

    permissions = [
        f"{up.permission.module}.{up.permission.action}"
        for up in user.permissions
    ]

    access_token = create_access_token(
        identity=user.username,
        additional_claims={"user_id": user.user_id},
    )
    return LoginResponse(user_id=user.user_id, access_token=access_token, permissions=permissions), 200
