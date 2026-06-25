from fastapi import APIRouter, Depends, HTTPException, status
from database.db import get_db
from schemas.notification import NotificationResponse
from utils.auth_helper import get_current_user
from typing import List

router = APIRouter(tags=["Notifications"])

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(db = Depends(get_db), current_user = Depends(get_current_user)):
    notifs = list(db.notifications.find({"user_id": current_user.id}).sort("created_at", -1))
    return notifs

@router.put("/notifications/{id}/read")
def read_notification(id: int, db = Depends(get_db), current_user = Depends(get_current_user)):
    result = db.notifications.update_one(
        {"id": id, "user_id": current_user.id},
        {"$set": {"is_read": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    return {"ok": True}
