from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models.notification import Notification
from schemas.notification import NotificationResponse
from utils.auth_helper import get_current_user
from typing import List

router = APIRouter(tags=["Notifications"])

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return notifs

@router.put("/notifications/{id}/read")
def read_notification(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    notif = db.query(Notification).filter(
        Notification.id == id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notif.is_read = True
    db.commit()
    return {"ok": True}
