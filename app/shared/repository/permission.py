from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import db
from app.shared.utils import time as time_utils

if TYPE_CHECKING:
    from app.shared.repository.user_permission import UserPermission


class Permission(db.Model):
    __tablename__ = 'permission'
    __table_args__ = (
        UniqueConstraint('module', 'action', name='unique_permission'),
        {'schema': 'py_mgmt_test'}
    )

    permission_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=time_utils.now_utc0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=time_utils.now_utc0,
        onupdate=time_utils.now_utc0,
    )

    users: Mapped[list["UserPermission"]] = relationship(
        back_populates='permission',
        cascade='all, delete-orphan',
    )
