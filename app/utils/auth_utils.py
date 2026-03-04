from flask_jwt_extended import get_jwt, get_jwt_identity

from ..models.user import User


def get_user_id_from_jwt() -> int | None:
    claims = get_jwt()
    user_id = claims.get("user_id")
    if user_id is not None:
        try:
            return int(user_id)
        except (TypeError, ValueError):
            return None

    username = get_jwt_identity()
    if not username:
        return None

    user = User.query.filter_by(username=username).first()
    return user.user_id if user else None
