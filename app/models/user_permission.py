from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from ..utils.time import now_utc0

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User


class UserPermission(db.Model):
    __tablename__ = 'user_permission'
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='unique_user_permission'),
        {'schema': 'py_mgmt_test'}
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('py_mgmt_test.user.user_id'), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey('py_mgmt_test.permission.permission_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now_utc0)

    user: Mapped["User"] = relationship(back_populates='permissions')
    permission: Mapped["Permission"] = relationship(back_populates='users')
