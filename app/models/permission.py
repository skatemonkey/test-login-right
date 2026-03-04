from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from ..extensions import db
from ..utils.time import now_utc8


class Permission(db.Model):
    __tablename__ = 'permission'
    __table_args__ = (
        UniqueConstraint('module', 'action', name='unique_permission'),
        {'schema': 'py_mgmt_test'}
    )

    permission_id = Column(Integer, primary_key=True, autoincrement=True)
    module = Column(String(50), nullable=False)
    action = Column(String(30), nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, nullable=False, default=now_utc8)

    users = relationship('UserPermission', back_populates='permission', cascade='all, delete-orphan')
