from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, index=True, nullable=True) # None for admin, string for students
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    year = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student", nullable=False) # "student" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)
