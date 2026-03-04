from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..extensions import db
from ..utils.time import now_utc0


class UserPermission(db.Model):
    __tablename__ = 'user_permission'
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='unique_user_permission'),
        {'schema': 'py_mgmt_test'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('py_mgmt_test.user.user_id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('py_mgmt_test.permission.permission_id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=now_utc0)

    user = relationship('User', back_populates='permissions')
    permission = relationship('Permission', back_populates='users')