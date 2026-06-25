from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from database.db import get_db, get_next_sequence_value
from schemas.request import RequestCreate, RequestApproveReject, RequestResponse
from services.notification_service import create_notification
from utils.auth_helper import get_admin_user, get_optional_user
from typing import List, Optional

router = APIRouter(tags=["Requests"])

@router.get("/requests")
def get_requests(
    status: Optional[str] = None,
    db = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    query = {}
    if current_user and current_user.role == "student":
        query["user_id"] = current_user.id
    if status:
        query["status"] = status
        
    requests = list(db.borrow_requests.find(query).sort("id", -1))
    
    response_list = []
    for r in requests:
        book = db.books.find_one({"id": r["book_id"]})
        user = db.users.find_one({"id": r["user_id"]})
        response_list.append({
            "id": r["id"],
            "book_id": r["book_id"],
            "user_id": r["user_id"],
            "request_date": r.get("request_date"),
            "preferred_date": r.get("preferred_date"),
            "note": r.get("note"),
            "status": r.get("status"),
            "admin_note": r.get("admin_note"),
            "action_time": r.get("action_time"),
            "created_at": r.get("created_at"),
            "book_title": book.get("title") if book else None,
            "author": book.get("author") if book else None,
            "genre": book.get("genre") if book else None,
            "book_available": book.get("available_copies", 0) if book else 0,
            "member_name": user.get("name") if user else None,
            "member_id": user.get("member_id") if user else None,
            "department": user.get("department") if user else None,
        })

    return response_list

@router.post("/requests")
def create_request(req: RequestCreate, db = Depends(get_db)):
    user = db.users.find_one({"member_id": req.member_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    book = db.books.find_one({"id": req.book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    dup = db.borrow_requests.find_one({
        "book_id": req.book_id,
        "user_id": user["id"],
        "status": "pending"
    })
    if dup:
        raise HTTPException(status_code=409, detail="Already have a pending request for this book")
        
    active_loan = db.loans.find_one({
        "book_id": req.book_id,
        "user_id": user["id"],
        "status": {"$in": ["active", "overdue"]}
    })
    if active_loan:
        raise HTTPException(status_code=409, detail="You already have an active loan for this book")
        
    settings = db.settings.find_one({"_id": "global"})
    max_books = settings.get("max_books", 3) if settings else 3
    active_loans_count = db.loans.count_documents({
        "user_id": user["id"],
        "status": {"$in": ["active", "overdue"]}
    })
    if active_loans_count >= max_books:
        raise HTTPException(
            status_code=400, 
            detail=f"You have reached the maximum limit of {max_books} borrowed books"
        )
        
    if book.get("available_copies", 0) < 1:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")
        
    new_id = get_next_sequence_value("requestid")
    new_request = {
        "id": new_id,
        "user_id": user["id"],
        "book_id": req.book_id,
        "preferred_date": req.preferred_date,
        "note": req.note,
        "status": "pending",
        "request_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "created_at": datetime.utcnow()
    }
    db.borrow_requests.insert_one(new_request)
    return {"ok": True, "id": new_id}

@router.post("/requests/{id}/approve")
@router.put("/requests/{id}/approve")
def approve_request(id: int, req: RequestApproveReject, db = Depends(get_db), current_user=Depends(get_admin_user)):
    r = db.borrow_requests.find_one({"id": id})
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if r["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {r['status']}")
        
    book = db.books.find_one({"id": r["book_id"]})
    if not book or book.get("available_copies", 0) < 1:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")
        
    settings = db.settings.find_one({"_id": "global"})
    max_books = settings.get("max_books", 3) if settings else 3
    active_loans_count = db.loans.count_documents({
        "user_id": r["user_id"],
        "status": {"$in": ["active", "overdue"]}
    })
    if active_loans_count >= max_books:
        raise HTTPException(
            status_code=400, 
            detail=f"User has reached the limit of {max_books} borrowed books"
        )

    db.borrow_requests.update_one({"id": id}, {"$set": {
        "status": "approved",
        "admin_note": req.admin_note,
        "action_time": datetime.utcnow()
    }})
    
    loan_days = settings.get("loan_period_days", 14) if settings else 14
    issue_date = datetime.utcnow().strftime("%Y-%m-%d")
    due_date = req.due_date or (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
    
    loan_id = get_next_sequence_value("loanid")
    loan = {
        "id": loan_id,
        "user_id": r["user_id"],
        "book_id": r["book_id"],
        "issue_date": issue_date,
        "due_date": due_date,
        "status": "active",
        "renew_count": 0,
        "fine_amount": 0.0,
        "request_id": r["id"]
    }
    db.loans.insert_one(loan)
    
    db.books.update_one({"id": r["book_id"]}, {"$inc": {"available_copies": -1}})
    
    create_notification(db, r["user_id"], f"Your request for '{book.get('title')}' was approved! Due date: {due_date}")
    
    return {"ok": True, "loan_id": loan_id}

@router.post("/requests/{id}/reject")
@router.put("/requests/{id}/reject")
def reject_request(id: int, req: RequestApproveReject, db = Depends(get_db), current_user=Depends(get_admin_user)):
    r = db.borrow_requests.find_one({"id": id})
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if r["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {r['status']}")
        
    db.borrow_requests.update_one({"id": id}, {"$set": {
        "status": "rejected",
        "admin_note": req.admin_note,
        "action_time": datetime.utcnow()
    }})
    
    book = db.books.find_one({"id": r["book_id"]})
    book_title = book.get("title") if book else "Book"
    
    create_notification(db, r["user_id"], f"Your request for '{book_title}' was rejected. Note: {req.admin_note or 'No reason provided'}")
    
    return {"ok": True}
