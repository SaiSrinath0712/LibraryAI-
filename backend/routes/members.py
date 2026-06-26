from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models.user import User
from models.loan import Loan
from utils.auth_helper import get_admin_user
from typing import List, Optional

router = APIRouter(tags=["Members"])

@router.get("/members")
def get_members(q: Optional[str] = "", db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    query = db.query(User).filter(User.role == "student")
    if q:
        search = f"%{q}%"
        query = query.filter(
            User.name.like(search) | 
            User.member_id.like(search) | 
            User.email.like(search)
        )
    members = query.order_by(User.name.asc()).all()
    
    result = []
    for m in members:
        active_loans = db.query(Loan).filter(
            Loan.user_id == m.id,
            Loan.status.in_(["active", "overdue"])
        ).count()
        total_loans = db.query(Loan).filter(Loan.user_id == m.id).count()
        
        result.append({
            "id": m.id,
            "name": m.name,
            "member_id": m.member_id,
            "email": m.email,
            "phone": m.phone,
            "department": m.department,
            "year": m.year,
            "role": m.role,
            "created_at": m.created_at,
            "active_loans": active_loans,
            "total_loans": total_loans
        })
    return result

@router.get("/members/{id}")
def get_member(id: str, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    user = None
    if id.isdigit():
        user = db.query(User).filter(User.id == int(id)).first()
    if not user:
        user = db.query(User).filter(User.member_id == id).first()
        
    if not user:
        raise HTTPException(status_code=404, detail="Member not found")
        
    loans = db.query(Loan).filter(Loan.user_id == user.id).order_by(Loan.id.desc()).all()
    
    loans_list = []
    for l in loans:
        loans_list.append({
            "id": l.id,
            "book_id": l.book_id,
            "book_title": l.book.title if l.book else "Unknown Book",
            "author": l.book.author if l.book else "",
            "genre": l.book.genre if l.book else "",
            "shelf": l.book.shelf_location if l.book else "",
            "issue_date": l.issue_date,
            "due_date": l.due_date,
            "return_date": l.return_date,
            "renewals": l.renew_count,
            "status": l.status,
            "fine": l.fine_amount
        })
        
    return {
        "id": user.id,
        "name": user.name,
        "member_id": user.member_id,
        "email": user.email,
        "phone": user.phone,
        "department": user.department,
        "year": user.year,
        "role": user.role,
        "created_at": user.created_at,
        "loans": loans_list
    }
