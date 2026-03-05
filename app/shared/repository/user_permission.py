from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import db
from app.shared.utils import time as time_utils

if TYPE_CHECKING:
    from app.shared.repository.permission import Permission
    from app.shared.repository.user import User


class UserPermission(db.Model):
    __tablename__ = 'user_permission'
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='unique_user_permission'),
        {'schema': 'py_mgmt_test'}
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('py_mgmt_test.user.user_id'), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey('py_mgmt_test.permission.permission_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=time_utils.now_utc0)

    user: Mapped["User"] = relationship(back_populates='permissions')
    permission: Mapped["Permission"] = relationship(back_populates='users')
