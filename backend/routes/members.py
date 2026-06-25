from fastapi import APIRouter, Depends, HTTPException, status
from database.db import get_db
from utils.auth_helper import get_admin_user
from typing import List, Optional
import re

router = APIRouter(tags=["Members"])

@router.get("/members")
def get_members(q: Optional[str] = "", db = Depends(get_db), current_user=Depends(get_admin_user)):
    query = {"role": "student"}
    if q:
        search_regex = re.compile(f".*{re.escape(q)}.*", re.IGNORECASE)
        query["$or"] = [
            {"name": search_regex},
            {"member_id": search_regex},
            {"email": search_regex}
        ]
    members = list(db.users.find(query).sort("name", 1))
    
    result = []
    for m in members:
        active_loans = db.loans.count_documents({
            "user_id": m["id"],
            "status": {"$in": ["active", "overdue"]}
        })
        total_loans = db.loans.count_documents({"user_id": m["id"]})
        
        result.append({
            "id": m["id"],
            "name": m.get("name"),
            "member_id": m.get("member_id"),
            "email": m.get("email"),
            "phone": m.get("phone"),
            "department": m.get("department"),
            "year": m.get("year"),
            "role": m.get("role"),
            "created_at": m.get("created_at"),
            "active_loans": active_loans,
            "total_loans": total_loans
        })
    return result

@router.get("/members/{id}")
def get_member(id: str, db = Depends(get_db), current_user=Depends(get_admin_user)):
    user = None
    if id.isdigit():
        user = db.users.find_one({"id": int(id)})
    if not user:
        user = db.users.find_one({"member_id": id})
        
    if not user:
        raise HTTPException(status_code=404, detail="Member not found")
        
    loans = list(db.loans.find({"user_id": user["id"]}).sort("id", -1))
    
    loans_list = []
    for l in loans:
        book = db.books.find_one({"id": l["book_id"]})
        loans_list.append({
            "id": l["id"],
            "book_id": l["book_id"],
            "book_title": book.get("title") if book else "Unknown Book",
            "author": book.get("author") if book else "",
            "genre": book.get("genre") if book else "",
            "shelf": book.get("shelf_location") if book else "",
            "issue_date": l.get("issue_date"),
            "due_date": l.get("due_date"),
            "return_date": l.get("return_date"),
            "renewals": l.get("renew_count", 0),
            "status": l.get("status"),
            "fine": l.get("fine_amount", 0.0)
        })
        
    return {
        "id": user["id"],
        "name": user.get("name"),
        "member_id": user.get("member_id"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "department": user.get("department"),
        "year": user.get("year"),
        "role": user.get("role"),
        "created_at": user.get("created_at"),
        "loans": loans_list
    }
