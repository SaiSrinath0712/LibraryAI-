from fastapi import APIRouter, Depends
from database.db import get_db
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
def get_settings(db = Depends(get_db)):
    settings = db.settings.find_one({"_id": "global"})
    if not settings:
        settings = {
            "_id": "global",
            "loan_period_days": 14,
            "max_books": 3,
            "fine_per_day": 2.0,
            "max_renewals": 2
        }
        db.settings.insert_one(settings)
        
    return {
        "id": 1,
        "loan_period_days": settings.get("loan_period_days", 14),
        "loan_days": settings.get("loan_period_days", 14),
        "max_books": settings.get("max_books", 3),
        "fine_per_day": settings.get("fine_per_day", 2.0),
        "max_renewals": settings.get("max_renewals", 2)
    }

@router.post("/settings")
def update_settings(req: SettingsUpdateSchema, db = Depends(get_db), current_user=Depends(get_admin_user)):
    settings = db.settings.find_one({"_id": "global"})
    if not settings:
        db.settings.insert_one({"_id": "global"})
        
    update_data = {}
    loan_days = req.loan_days if req.loan_days is not None else req.loan_period_days
    if loan_days is not None:
        update_data["loan_period_days"] = loan_days
    if req.max_books is not None:
        update_data["max_books"] = req.max_books
    if req.fine_per_day is not None:
        update_data["fine_per_day"] = req.fine_per_day
    if req.max_renewals is not None:
        update_data["max_renewals"] = req.max_renewals
        
    if update_data:
        db.settings.update_one({"_id": "global"}, {"$set": update_data})
        
    return {"ok": True}
