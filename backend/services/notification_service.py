from sqlalchemy.orm import Session
from models.notification import Notification

def create_notification(db: Session, user_id: int, message: str) -> Notification:
    notif = Notification(user_id=user_id, message=message, is_read=False)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
