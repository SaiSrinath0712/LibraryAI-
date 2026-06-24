from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.settings import Settings
from pydantic import BaseModel
from utils.auth_helper import get_admin_user
from typing import Optional

router = APIRouter(tags=["Settings"])

class SettingsUpdateSchema(BaseModel):
    loan_days: Optional[int] = None
    loan_period_days: Optional[int] = None
    max_books: Optional[int] = None
    fine_per_day: Optional[float] = None
    max_renewals: Optional[int] = None

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings(
            loan_period_days=14,
            max_books=3,
            fine_per_day=2.0,
            max_renewals=2
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    return {
        "id": settings.id,
        "loan_period_days": settings.loan_period_days,
        "loan_days": settings.loan_period_days,
        "max_books": settings.max_books,
        "fine_per_day": settings.fine_per_day,
        "max_renewals": settings.max_renewals
    }

@router.post("/settings")
def update_settings(req: SettingsUpdateSchema, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        
    loan_days = req.loan_days if req.loan_days is not None else req.loan_period_days
    if loan_days is not None:
        settings.loan_period_days = loan_days
    if req.max_books is not None:
        settings.max_books = req.max_books
    if req.fine_per_day is not None:
        settings.fine_per_day = req.fine_per_day
    if req.max_renewals is not None:
        settings.max_renewals = req.max_renewals
        
    db.commit()
    return {"ok": True}
