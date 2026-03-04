from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import db
from app.common.utils.time import now_utc0

if TYPE_CHECKING:
    from app.common.repository.user import User


class Notification(db.Model):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'py_mgmt_test'}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('py_mgmt_test.user.user_id'), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now_utc0)

    user: Mapped["User"] = relationship(back_populates='notifications')
