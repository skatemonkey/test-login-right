from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import Unauthorized


def current_user_id() -> int:
    raw_identity = get_jwt_identity()
    try:
        return int(raw_identity)
    except (TypeError, ValueError) as exc:
        raise Unauthorized("Invalid token identity") from exc
