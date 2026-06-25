from database.db import get_next_sequence_value
from datetime import datetime

def create_notification(db, user_id: int, message: str) -> dict:
    new_id = get_next_sequence_value("notificationid")
    notif = {
        "id": new_id,
        "user_id": user_id,
        "message": message,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    db.notifications.insert_one(notif)
    return notif
