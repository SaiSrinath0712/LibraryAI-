from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database.db import get_db
from models.loan import Loan
from models.book import Book
from models.user import User
from models.settings import Settings
from schemas.loan import LoanIssueRequest, LoanRenewReturnRequest, LoanResponse
from services.fine_service import calculate_fine
from services.notification_service import create_notification
from utils.auth_helper import get_admin_user
from typing import List, Optional

router = APIRouter(tags=["Loans"])

def refresh_loans_status(db: Session):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    active_loans = db.query(Loan).filter(Loan.status.in_(["active", "overdue"])).all()
    for l in active_loans:
        if l.due_date < today:
            l.status = "overdue"
        else:
            l.status = "active"
        l.fine_amount = calculate_fine(l.due_date, db=db)
    db.commit()

@router.get("/loans", response_model=List[LoanResponse])
def get_loans(
    status: Optional[str] = None,
    member_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    refresh_loans_status(db)
    
    query = db.query(Loan)
    if status:
        query = query.filter(Loan.status == status)
        
    if member_id:
        user = db.query(User).filter(User.member_id == member_id).first()
        if user:
            query = query.filter(Loan.user_id == user.id)
        else:
            return []
            
    loans = query.order_by(Loan.id.desc()).all()
    
    response_list = []
    for l in loans:
        response_list.append({
            "id": l.id,
            "user_id": l.user_id,
            "book_id": l.book_id,
            "issue_date": l.issue_date,
            "due_date": l.due_date,
            "return_date": l.return_date,
            "renew_count": l.renew_count,
            "renewals": l.renew_count,
            "status": l.status,
            "fine_amount": l.fine_amount,
            "fine": l.fine_amount,
            "request_id": l.request_id,
            "book_title": l.book.title if l.book else None,
            "author": l.book.author if l.book else None,
            "genre": l.book.genre if l.book else None,
            "shelf": l.book.shelf_location if l.book else None,
            "isbn": l.book.isbn if l.book else None,
            "member_name": l.user.name if l.user else None,
            "member_id": l.user.member_id if l.user else None,
            "department": l.user.department if l.user else None,
        })

    return response_list

@router.post("/loans/issue", response_model=LoanResponse)
def issue_loan(req: LoanIssueRequest, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    user = db.query(User).filter(User.member_id == req.member_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    book = db.query(Book).filter(Book.id == req.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")
        
    dup = db.query(Loan).filter(
        Loan.book_id == req.book_id,
        Loan.user_id == user.id,
        Loan.status.in_(["active", "overdue"])
    ).first()
    if dup:
        raise HTTPException(status_code=409, detail="User already has an active loan for this book")
        
    settings = db.query(Settings).first()
    max_books = settings.max_books if settings else 3
    active_count = db.query(Loan).filter(
        Loan.user_id == user.id,
        Loan.status.in_(["active", "overdue"])
    ).count()
    if active_count >= max_books:
        raise HTTPException(status_code=400, detail=f"User has reached the limit of {max_books} books")
        
    loan_days = settings.loan_period_days if settings else 14
    issue_date = datetime.utcnow().strftime("%Y-%m-%d")
    due_date = req.due_date or (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
    
    loan = Loan(
        user_id=user.id,
        book_id=req.book_id,
        issue_date=issue_date,
        due_date=due_date,
        status="active"
    )
    db.add(loan)
    
    book.available_copies -= 1
    
    db.commit()
    db.refresh(loan)
    return loan

@router.post("/loans/{id}/return")
@router.post("/loans/return")
def return_loan(id: Optional[int] = None, req: Optional[LoanRenewReturnRequest] = None, db: Session = Depends(get_db)):
    loan_id = id
    if req and req.loan_id:
        loan_id = req.loan_id
        
    if not loan_id:
        raise HTTPException(status_code=400, detail="Loan ID is required")
        
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    if loan.status == "returned":
        raise HTTPException(status_code=400, detail="Book already returned")
        
    today = datetime.utcnow().strftime("%Y-%m-%d")
    fine = calculate_fine(loan.due_date, today, db=db)
    
    loan.status = "returned"
    loan.return_date = today
    loan.fine_amount = fine
    
    book = loan.book
    if book:
        book.available_copies += 1
        
    create_notification(db, loan.user_id, f"You returned '{book.title if book else 'Book'}' successfully. Fine: ₹{fine}")
    
    db.commit()
    return {"ok": True, "fine": fine, "return_date": today}

@router.post("/loans/{id}/renew")
@router.post("/loans/renew")
def renew_loan(id: Optional[int] = None, req: Optional[LoanRenewReturnRequest] = None, db: Session = Depends(get_db)):
    loan_id = id
    if req and req.loan_id:
        loan_id = req.loan_id
        
    if not loan_id:
        raise HTTPException(status_code=400, detail="Loan ID is required")
        
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    if loan.status == "returned":
        raise HTTPException(status_code=400, detail="Cannot renew returned book")
        
    settings = db.query(Settings).first()
    max_renewals = settings.max_renewals if settings else 2
    if loan.renew_count >= max_renewals:
        raise HTTPException(status_code=400, detail=f"Maximum of {max_renewals} renewals allowed")
        
    loan_days = settings.loan_period_days if settings else 14
    new_due = (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
    
    loan.due_date = new_due
    loan.status = "active"
    loan.renew_count += 1
    
    create_notification(db, loan.user_id, f"Your loan for '{loan.book.title}' has been renewed. New due date: {new_due}")
    
    db.commit()
    return {"ok": True, "new_due": new_due}
