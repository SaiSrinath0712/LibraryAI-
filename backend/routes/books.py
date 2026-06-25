from fastapi import APIRouter, Depends, HTTPException, status
from database.db import get_db, get_next_sequence_value
from schemas.book import BookCreate, BookResponse
from utils.auth_helper import get_admin_user
from typing import List, Optional
import re
from datetime import datetime

router = APIRouter(tags=["Books"])

def serialize_book(book: dict, db) -> dict:
    borrow_count = db.loans.count_documents({"book_id": book["id"]})
    return {
        "id": book["id"],
        "title": book["title"],
        "author": book["author"],
        "isbn": book.get("isbn"),
        "genre": book.get("genre"),
        "publisher": book.get("publisher"),
        "year": book.get("year"),
        "copies": book.get("copies", 1),
        "available_copies": book.get("available_copies", 1),
        "available": book.get("available_copies", 1),
        "shelf_location": book.get("shelf_location"),
        "shelf": book.get("shelf_location"),
        "rating": book.get("rating", 4.0),
        "description": book.get("description"),
        "tags": book.get("tags"),
        "borrow_count": borrow_count,
        "created_at": book.get("created_at"),
    }

@router.get("/books", response_model=List[BookResponse])
def get_books(
    q: Optional[str] = "",
    genre: Optional[str] = None,
    available: Optional[str] = None,
    db = Depends(get_db)
):
    filter_query = {}
    if q:
        search_regex = re.compile(f".*{re.escape(q)}.*", re.IGNORECASE)
        filter_query["$or"] = [
            {"title": search_regex},
            {"author": search_regex},
            {"genre": search_regex},
            {"isbn": search_regex}
        ]
    if genre:
        filter_query["genre"] = genre
    if available == "1" or available == "true":
        filter_query["available_copies"] = {"$gt": 0}
        
    books = list(db.books.find(filter_query).sort("title", 1))
    return [serialize_book(b, db) for b in books]

@router.get("/books/{id}", response_model=BookResponse)
def get_book(id: int, db = Depends(get_db)):
    book = db.books.find_one({"id": id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return serialize_book(book, db)

@router.post("/books", response_model=BookResponse)
def create_book(req: BookCreate, db = Depends(get_db), current_user=Depends(get_admin_user)):
    if req.isbn:
        existing = db.books.find_one({"isbn": req.isbn})
        if existing:
            raise HTTPException(status_code=400, detail="ISBN already exists")
            
    new_id = get_next_sequence_value("bookid")
    book = {
        "id": new_id,
        "title": req.title,
        "author": req.author,
        "isbn": req.isbn,
        "genre": req.genre,
        "publisher": req.publisher,
        "year": req.year,
        "copies": req.copies,
        "available_copies": req.copies,
        "shelf_location": req.shelf_location,
        "rating": req.rating or 4.0,
        "description": req.description,
        "tags": req.tags,
        "created_at": datetime.utcnow()
    }
    db.books.insert_one(book)
    return serialize_book(book, db)

@router.put("/books/{id}")
def update_book(id: int, req: BookCreate, db = Depends(get_db), current_user=Depends(get_admin_user)):
    book = db.books.find_one({"id": id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if req.isbn and req.isbn != book.get("isbn"):
        existing = db.books.find_one({"isbn": req.isbn})
        if existing:
            raise HTTPException(status_code=400, detail="ISBN already exists")
            
    lent_copies = book.get("copies", 1) - book.get("available_copies", 1)
    new_available = req.copies - lent_copies
    if new_available < 0:
        raise HTTPException(status_code=400, detail="Cannot reduce copies below currently active loans")
        
    db.books.update_one(
        {"id": id},
        {"$set": {
            "title": req.title,
            "author": req.author,
            "isbn": req.isbn,
            "genre": req.genre,
            "publisher": req.publisher,
            "year": req.year,
            "copies": req.copies,
            "available_copies": new_available,
            "shelf_location": req.shelf_location,
            "rating": req.rating or 4.0,
            "description": req.description,
            "tags": req.tags
        }}
    )
    return {"ok": True, "message": "Book updated successfully"}

@router.delete("/books/{id}")
def delete_book(id: int, db = Depends(get_db), current_user=Depends(get_admin_user)):
    result = db.books.delete_one({"id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"ok": True, "message": "Book deleted successfully"}
