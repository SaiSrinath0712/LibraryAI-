from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database.db import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, index=True, nullable=True)
    genre = Column(String, nullable=False, index=True)
    publisher = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    shelf_location = Column(String, nullable=True)
    rating = Column(Float, default=4.0, nullable=True)
    description = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def available(self) -> int:
        return self.available_copies
