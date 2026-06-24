from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.db import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    issue_date = Column(String, nullable=False) # YYYY-MM-DD
    due_date = Column(String, nullable=False) # YYYY-MM-DD
    return_date = Column(String, nullable=True) # YYYY-MM-DD
    renew_count = Column(Integer, default=0, nullable=False)
    status = Column(String, default="active", nullable=False) # 'active', 'returned', 'overdue'
    fine_amount = Column(Float, default=0.0, nullable=False)
    request_id = Column(Integer, ForeignKey("borrow_requests.id"), nullable=True)

    user = relationship("User")
    book = relationship("Book")

    @property
    def renewals(self) -> int:
        return self.renew_count

    @property
    def fine(self) -> float:
        return self.fine_amount
