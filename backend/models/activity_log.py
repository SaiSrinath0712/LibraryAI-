from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database.db import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
