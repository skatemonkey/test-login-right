from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..extensions import db
from ..utils.time import now_utc8

UTC8 = timezone(timedelta(hours=8))


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'py_mgmt_test'}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=now_utc8)
    updated_at = Column(DateTime, nullable=False, default=now_utc8, onupdate=now_utc8)

    permissions = relationship('UserPermission', back_populates='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
