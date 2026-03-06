from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from app.shared.repository.user import User
from app.shared.schemas.auth_schema import ErrorResponse, LoginRequest, LoginResponse


def login(req: LoginRequest):
    user = User.query.filter_by(username=req.username).first()
    if not user or not _verify_password(req.password, user.password_hash):
        return ErrorResponse(error="Invalid credentials"), 401

    permissions = [
        f"{up.permission.module}.{up.permission.action}"
        for up in user.permissions
    ]

    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"username": user.username}
    )
    return LoginResponse(userId=user.user_id, username=user.username, accessToken=access_token,
                         permissions=permissions), 200


def _verify_password(raw_password: str, stored_hash: str | bytes) -> bool:
    if not raw_password or not stored_hash:
        return False

    try:
        normalized_hash = (
            stored_hash.decode("utf-8")
            if isinstance(stored_hash, (bytes, bytearray))
            else str(stored_hash)
        )
        return check_password_hash(normalized_hash, raw_password)
    except (TypeError, ValueError):
        return False
