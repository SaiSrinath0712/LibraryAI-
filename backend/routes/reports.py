from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.loan import Loan
from models.user import User
from models.book import Book
from typing import List, Dict, Any

router = APIRouter(tags=["Reports"])

@router.get("/reports/overdue")
def get_reports_overdue(db: Session = Depends(get_db)):
    overdue_loans = db.query(Loan).filter(Loan.status == "overdue").all()
    result = []
    for l in overdue_loans:
        result.append({
            "book_title": l.book.title if l.book else "Unknown Book",
            "member_name": l.user.name if l.user else "Unknown Member",
            "member_id": l.user.member_id if l.user else "",
            "due_date": l.due_date,
            "fine_amount": l.fine_amount
        })
    return result

@router.get("/reports/fines")
def get_reports_fines(db: Session = Depends(get_db)):
    overdue_loans = db.query(Loan).filter(Loan.fine_amount > 0).all()
    result = []
    for l in overdue_loans:
        result.append({
            "book_title": l.book.title if l.book else "Unknown Book",
            "member_name": l.user.name if l.user else "Unknown Member",
            "member_id": l.user.member_id if l.user else "",
            "due_date": l.due_date,
            "fine_amount": l.fine_amount
        })
    return result

@router.get("/reports/members")
def get_reports_members(db: Session = Depends(get_db)):
    members = db.query(User).filter(User.role == "student").all()
    result = []
    for m in members:
        active_loans = db.query(Loan).filter(
            Loan.user_id == m.id,
            Loan.status.in_(["active", "overdue"])
        ).count()
        result.append({
            "name": m.name,
            "member_id": m.member_id,
            "department": m.department,
            "year": m.year,
            "email": m.email,
            "phone": m.phone,
            "active_loans": active_loans
        })
    return result

@router.get("/reports/books")
def get_reports_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    result = []
    for b in books:
        result.append({
            "title": b.title,
            "author": b.author,
            "genre": b.genre,
            "isbn": b.isbn,
            "copies": b.copies,
            "available": b.available_copies,
            "shelf": b.shelf_location
        })
    return result
