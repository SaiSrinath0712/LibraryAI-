from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database.db import get_db
from models.request import BorrowRequest
from models.book import Book
from models.user import User
from models.loan import Loan
from models.settings import Settings
from schemas.request import RequestCreate, RequestApproveReject, RequestResponse
from services.notification_service import create_notification
from utils.auth_helper import get_admin_user, get_optional_user
from typing import List, Optional

router = APIRouter(tags=["Requests"])

@router.get("/requests")
def get_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    query = db.query(BorrowRequest)
    if current_user and current_user.role == "student":
        query = query.filter(BorrowRequest.user_id == current_user.id)
    if status:
        query = query.filter(BorrowRequest.status == status)
    requests = query.order_by(BorrowRequest.id.desc()).all()
    
    response_list = []
    for r in requests:
        response_list.append({
            "id": r.id,
            "book_id": r.book_id,
            "user_id": r.user_id,
            "request_date": r.request_date,
            "preferred_date": r.preferred_date,
            "note": r.note,
            "status": r.status,
            "admin_note": r.admin_note,
            "action_time": r.action_time,
            "created_at": r.created_at,
            "book_title": r.book.title if r.book else None,
            "author": r.book.author if r.book else None,
            "genre": r.book.genre if r.book else None,
            "book_available": r.book.available_copies if r.book else 0,
            "member_name": r.user.name if r.user else None,
            "member_id": r.user.member_id if r.user else None,
            "department": r.user.department if r.user else None,
        })

    return response_list

@router.post("/requests")
def create_request(req: RequestCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.member_id == req.member_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    book = db.query(Book).filter(Book.id == req.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    dup = db.query(BorrowRequest).filter(
        BorrowRequest.book_id == req.book_id,
        BorrowRequest.user_id == user.id,
        BorrowRequest.status == "pending"
    ).first()
    if dup:
        raise HTTPException(status_code=409, detail="Already have a pending request for this book")
        
    active_loan = db.query(Loan).filter(
        Loan.book_id == req.book_id,
        Loan.user_id == user.id,
        Loan.status.in_(["active", "overdue"])
    ).first()
    if active_loan:
        raise HTTPException(status_code=409, detail="You already have an active loan for this book")
        
    settings = db.query(Settings).first()
    max_books = settings.max_books if settings else 3
    active_loans_count = db.query(Loan).filter(
        Loan.user_id == user.id,
        Loan.status.in_(["active", "overdue"])
    ).count()
    if active_loans_count >= max_books:
        raise HTTPException(
            status_code=400, 
            detail=f"You have reached the maximum limit of {max_books} borrowed books"
        )
        
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")
        
    new_request = BorrowRequest(
        user_id=user.id,
        book_id=req.book_id,
        preferred_date=req.preferred_date,
        note=req.note,
        status="pending"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"ok": True, "id": new_request.id}

@router.post("/requests/{id}/approve")
@router.put("/requests/{id}/approve")
def approve_request(id: int, req: RequestApproveReject, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    r = db.query(BorrowRequest).filter(BorrowRequest.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if r.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {r.status}")
        
    book = r.book
    if not book or book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")
        
    settings = db.query(Settings).first()
    max_books = settings.max_books if settings else 3
    active_loans_count = db.query(Loan).filter(
        Loan.user_id == r.user_id,
        Loan.status.in_(["active", "overdue"])
    ).count()
    if active_loans_count >= max_books:
        raise HTTPException(
            status_code=400, 
            detail=f"User has reached the limit of {max_books} borrowed books"
        )

    r.status = "approved"
    r.admin_note = req.admin_note
    r.action_time = datetime.utcnow()
    
    loan_days = settings.loan_period_days if settings else 14
    issue_date = datetime.utcnow().strftime("%Y-%m-%d")
    due_date = req.due_date or (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
    
    loan = Loan(
        user_id=r.user_id,
        book_id=r.book_id,
        issue_date=issue_date,
        due_date=due_date,
        status="active",
        renew_count=0,
        fine_amount=0.0,
        request_id=r.id
    )
    db.add(loan)
    
    book.available_copies -= 1
    
    create_notification(db, r.user_id, f"Your request for '{book.title}' was approved! Due date: {due_date}")
    
    db.commit()
    return {"ok": True, "loan_id": loan.id}

@router.post("/requests/{id}/reject")
@router.put("/requests/{id}/reject")
def reject_request(id: int, req: RequestApproveReject, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    r = db.query(BorrowRequest).filter(BorrowRequest.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if r.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {r.status}")
        
    r.status = "rejected"
    r.admin_note = req.admin_note
    r.action_time = datetime.utcnow()
    
    create_notification(db, r.user_id, f"Your request for '{r.book.title}' was rejected. Note: {req.admin_note or 'No reason provided'}")
    
    db.commit()
    return {"ok": True}
