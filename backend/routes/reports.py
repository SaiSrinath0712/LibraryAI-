from fastapi import APIRouter, Depends
from database.db import get_db
from typing import List, Dict, Any

router = APIRouter(tags=["Reports"])

@router.get("/reports/overdue")
def get_reports_overdue(db = Depends(get_db)):
    overdue_loans = list(db.loans.find({"status": "overdue"}))
    result = []
    for l in overdue_loans:
        book = db.books.find_one({"id": l["book_id"]})
        user = db.users.find_one({"id": l["user_id"]})
        result.append({
            "book_title": book.get("title") if book else "Unknown Book",
            "member_name": user.get("name") if user else "Unknown Member",
            "member_id": user.get("member_id") if user else "",
            "due_date": l.get("due_date"),
            "fine_amount": l.get("fine_amount", 0.0)
        })
    return result

@router.get("/reports/fines")
def get_reports_fines(db = Depends(get_db)):
    fine_loans = list(db.loans.find({"fine_amount": {"$gt": 0}}))
    result = []
    for l in fine_loans:
        book = db.books.find_one({"id": l["book_id"]})
        user = db.users.find_one({"id": l["user_id"]})
        result.append({
            "book_title": book.get("title") if book else "Unknown Book",
            "member_name": user.get("name") if user else "Unknown Member",
            "member_id": user.get("member_id") if user else "",
            "due_date": l.get("due_date"),
            "fine_amount": l.get("fine_amount", 0.0)
        })
    return result

@router.get("/reports/members")
def get_reports_members(db = Depends(get_db)):
    members = list(db.users.find({"role": "student"}))
    result = []
    for m in members:
        active_loans = db.loans.count_documents({
            "user_id": m["id"],
            "status": {"$in": ["active", "overdue"]}
        })
        result.append({
            "name": m.get("name"),
            "member_id": m.get("member_id"),
            "department": m.get("department"),
            "year": m.get("year"),
            "email": m.get("email"),
            "phone": m.get("phone"),
            "active_loans": active_loans
        })
    return result

@router.get("/reports/books")
def get_reports_books(db = Depends(get_db)):
    books = list(db.books.find({}))
    result = []
    for b in books:
        result.append({
            "title": b.get("title"),
            "author": b.get("author"),
            "genre": b.get("genre"),
            "isbn": b.get("isbn"),
            "copies": b.get("copies", 1),
            "available": b.get("available_copies", 1),
            "shelf": b.get("shelf_location")
        })
    return result
