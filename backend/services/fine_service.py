from datetime import datetime

def calculate_fine(due_date_str: str, return_date_str: str = None, db = None) -> float:
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
        settings = db.settings.find_one({"_id": "global"})
        if settings:
            fine_per_day = settings.get("fine_per_day", 2.0)

    return float(days_overdue * fine_per_day)
