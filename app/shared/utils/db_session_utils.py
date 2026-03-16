from app.core import db


def commit_session() -> None:
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def commit_and_refresh(instance):
    commit_session()
    db.session.refresh(instance)
    return instance
