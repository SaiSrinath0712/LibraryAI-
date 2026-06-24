from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class BorrowRequest(Base):
    __tablename__ = "borrow_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    request_date = Column(DateTime, default=datetime.utcnow)
    preferred_date = Column(String, nullable=True) # YYYY-MM-DD
    note = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False) # 'pending', 'approved', 'rejected'
    admin_note = Column(String, nullable=True)
    action_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    book = relationship("Book")
