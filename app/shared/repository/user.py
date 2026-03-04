from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import db
from app.shared.utils.time import now_utc0

if TYPE_CHECKING:
    from app.shared.repository.notification import Notification
    from .user_permission import UserPermission


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'py_mgmt_test'}

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now_utc0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=now_utc0,
        onupdate=now_utc0,
    )

    permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
    )
