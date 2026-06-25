from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from database.db import get_db, get_next_sequence_value
from schemas.loan import LoanIssueRequest, LoanRenewReturnRequest, LoanResponse
from services.fine_service import calculate_fine
from services.notification_service import create_notification
from utils.auth_helper import get_admin_user
from typing import List, Optional

router = APIRouter(tags=["Loans"])

def refresh_loans_status(db):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    active_loans = list(db.loans.find({"status": {"$in": ["active", "overdue"]}}))
    for l in active_loans:
        status = "overdue" if l["due_date"] < today else "active"
        fine_amount = calculate_fine(l["due_date"], db=db)
        db.loans.update_one({"id": l["id"]}, {"$set": {"status": status, "fine_amount": fine_amount}})

@router.get("/loans", response_model=List[LoanResponse])
def get_loans(
    status: Optional[str] = None,
    member_id: Optional[str] = None,
    db = Depends(get_db)
):
    refresh_loans_status(db)
    
    query = {}
    if status:
        query["status"] = status
        
    if member_id:
        user = db.users.find_one({"member_id": member_id})
        if user:
            query["user_id"] = user["id"]
        else:
            return []
            
    loans = list(db.loans.find(query).sort("id", -1))
    
    response_list = []
    for l in loans:
        book = db.books.find_one({"id": l["book_id"]})
        user = db.users.find_one({"id": l["user_id"]})
        response_list.append({
            "id": l["id"],
            "user_id": l["user_id"],
            "book_id": l["book_id"],
            "issue_date": l.get("issue_date"),
            "due_date": l.get("due_date"),
            "return_date": l.get("return_date"),
            "renew_count": l.get("renew_count", 0),
            "renewals": l.get("renew_count", 0),
            "status": l.get("status"),
            "fine_amount": l.get("fine_amount", 0.0),
            "fine": l.get("fine_amount", 0.0),
            "request_id": l.get("request_id"),
            "book_title": book.get("title") if book else None,
            "author": book.get("author") if book else None,
            "genre": book.get("genre") if book else None,
            "shelf": book.get("shelf_location") if book else None,
            "isbn": book.get("isbn") if book else None,
            "member_name": user.get("name") if user else None,
            "member_id": user.get("member_id") if user else None,
            "department": user.get("department") if user else None,
        })

    return response_list

@router.post("/loans/issue", response_model=LoanResponse)
def issue_loan(req: LoanIssueRequest, db = Depends(get_db), current_user=Depends(get_admin_user)):
    user = db.users.find_one({"member_id": req.member_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    book = db.books.find_one({"id": req.book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if book.get("available_copies", 0) < 1:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")
        
    dup = db.loans.find_one({
        "book_id": req.book_id,
        "user_id": user["id"],
        "status": {"$in": ["active", "overdue"]}
    })
    if dup:
        raise HTTPException(status_code=409, detail="User already has an active loan for this book")
        
    settings = db.settings.find_one({"_id": "global"})
    max_books = settings.get("max_books", 3) if settings else 3
    active_count = db.loans.count_documents({
        "user_id": user["id"],
        "status": {"$in": ["active", "overdue"]}
    })
    if active_count >= max_books:
        raise HTTPException(status_code=400, detail=f"User has reached the limit of {max_books} books")
        
    loan_days = settings.get("loan_period_days", 14) if settings else 14
    issue_date = datetime.utcnow().strftime("%Y-%m-%d")
    due_date = req.due_date or (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
    
    new_id = get_next_sequence_value("loanid")
    loan = {
        "id": new_id,
        "user_id": user["id"],
        "book_id": req.book_id,
        "issue_date": issue_date,
        "due_date": due_date,
        "status": "active",
        "renew_count": 0,
        "fine_amount": 0.0
    }
    db.loans.insert_one(loan)
    
    db.books.update_one({"id": req.book_id}, {"$inc": {"available_copies": -1}})
    return loan

@router.post("/loans/{id}/return")
@router.post("/loans/return")
def return_loan(id: Optional[int] = None, req: Optional[LoanRenewReturnRequest] = None, db = Depends(get_db)):
    loan_id = id
    if req and req.loan_id:
        loan_id = req.loan_id
        
    if not loan_id:
        raise HTTPException(status_code=400, detail="Loan ID is required")
        
    loan = db.loans.find_one({"id": loan_id})
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    if loan["status"] == "returned":
        raise HTTPException(status_code=400, detail="Book already returned")
        
    today = datetime.utcnow().strftime("%Y-%m-%d")
    fine = calculate_fine(loan["due_date"], today, db=db)
    
    db.loans.update_one({"id": loan_id}, {"$set": {
        "status": "returned",
        "return_date": today,
        "fine_amount": fine
    }})
    
    book = db.books.find_one({"id": loan["book_id"]})
    if book:
        db.books.update_one({"id": book["id"]}, {"$inc": {"available_copies": 1}})
        
    create_notification(db, loan["user_id"], f"You returned '{book.get('title') if book else 'Book'}' successfully. Fine: ₹{fine}")
    
    return {"ok": True, "fine": fine, "return_date": today}

@router.post("/loans/{id}/renew")
@router.post("/loans/renew")
def renew_loan(id: Optional[int] = None, req: Optional[LoanRenewReturnRequest] = None, db = Depends(get_db)):
    loan_id = id
    if req and req.loan_id:
        loan_id = req.loan_id
        
    if not loan_id:
        raise HTTPException(status_code=400, detail="Loan ID is required")
        
    loan = db.loans.find_one({"id": loan_id})
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    if loan["status"] == "returned":
        raise HTTPException(status_code=400, detail="Cannot renew returned book")
        
    settings = db.settings.find_one({"_id": "global"})
    max_renewals = settings.get("max_renewals", 2) if settings else 2
    renew_count = loan.get("renew_count", 0)
    if renew_count >= max_renewals:
        raise HTTPException(status_code=400, detail=f"Maximum of {max_renewals} renewals allowed")
        
    loan_days = settings.get("loan_period_days", 14) if settings else 14
    new_due = (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
    
    db.loans.update_one({"id": loan_id}, {"$set": {
        "due_date": new_due,
        "status": "active"
    }, "$inc": {"renew_count": 1}})
    
    book = db.books.find_one({"id": loan["book_id"]})
    book_title = book.get("title") if book else "Book"
    create_notification(db, loan["user_id"], f"Your loan for '{book_title}' has been renewed. New due date: {new_due}")
    
    return {"ok": True, "new_due": new_due}
