from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..extensions import db
from ..utils.time import now_utc8


class Notification(db.Model):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'py_mgmt_test'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('py_mgmt_test.user.user_id'), nullable=False)
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, nullable=False, default=now_utc8)

    user = relationship('User', back_populates='notifications')
