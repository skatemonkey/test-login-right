from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    __table_args__ = {'schema': 'py_mgmt_test'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    ip = Column(String(45))
    device = Column(String(255))
    created_time = Column(DateTime, default=datetime.utcnow)
    module = Column(String(100))
    action = Column(String(100))
    details = Column(Text)