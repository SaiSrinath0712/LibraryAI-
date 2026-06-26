from datetime import datetime
from sqlalchemy.orm import Session
from models.settings import Settings

def calculate_fine(due_date_str: str, return_date_str: str = None, db: Session = None) -> float:
    end_date_str = return_date_str or datetime.utcnow().strftime("%Y-%m-%d")
    
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return 0.0

    if end_date <= due_date:
        return 0.0

    days_overdue = (end_date - due_date).days
    
    fine_per_day = 2.0
    if db:
        settings = db.query(Settings).first()
        if settings:
            fine_per_day = settings.fine_per_day

    return float(days_overdue * fine_per_day)
