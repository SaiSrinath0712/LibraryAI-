from sqlalchemy import Column, Integer, Float
from database.db import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    loan_period_days = Column(Integer, default=14, nullable=False)
    max_books = Column(Integer, default=3, nullable=False)
    fine_per_day = Column(Float, default=2.0, nullable=False)
    max_renewals = Column(Integer, default=2, nullable=False)
