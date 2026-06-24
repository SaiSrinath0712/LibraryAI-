from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from models.book import Book
from models.loan import Loan
from schemas.book import BookCreate, BookResponse
from utils.auth_helper import get_admin_user
from typing import List, Optional

router = APIRouter(tags=["Books"])

def serialize_book(book: Book, db: Session) -> dict:
    borrow_count = db.query(Loan).filter(Loan.book_id == book.id).count()
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "genre": book.genre,
        "publisher": book.publisher,
        "year": book.year,
        "copies": book.copies,
        "available_copies": book.available_copies,
        "available": book.available_copies,
        "shelf_location": book.shelf_location,
        "shelf": book.shelf_location,
        "rating": book.rating,
        "description": book.description,
        "tags": book.tags,
        "borrow_count": borrow_count,
        "created_at": book.created_at,
    }

@router.get("/books", response_model=List[BookResponse])
def get_books(
    q: Optional[str] = "",
    genre: Optional[str] = None,
    available: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Book)
    if q:
        search = f"%{q}%"
        query = query.filter(
            Book.title.like(search) | 
            Book.author.like(search) | 
            Book.genre.like(search) | 
            Book.isbn.like(search)
        )
    if genre:
        query = query.filter(Book.genre == genre)
    if available == "1" or available == "true":
        query = query.filter(Book.available_copies > 0)
        
    books = query.order_by(Book.title.asc()).all()
    return [serialize_book(b, db) for b in books]

@router.get("/books/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return serialize_book(book, db)

@router.post("/books", response_model=BookResponse)
def create_book(req: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    if req.isbn:
        existing = db.query(Book).filter(Book.isbn == req.isbn).first()
        if existing:
            raise HTTPException(status_code=400, detail="ISBN already exists")
            
    book = Book(
        title=req.title,
        author=req.author,
        isbn=req.isbn,
        genre=req.genre,
        publisher=req.publisher,
        year=req.year,
        copies=req.copies,
        available_copies=req.copies,
        shelf_location=req.shelf_location,
        rating=req.rating or 4.0,
        description=req.description,
        tags=req.tags
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return serialize_book(book, db)

@router.put("/books/{id}")
def update_book(id: int, req: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if req.isbn and req.isbn != book.isbn:
        existing = db.query(Book).filter(Book.isbn == req.isbn).first()
        if existing:
            raise HTTPException(status_code=400, detail="ISBN already exists")
            
    lent_copies = book.copies - book.available_copies
    new_available = req.copies - lent_copies
    if new_available < 0:
        raise HTTPException(status_code=400, detail="Cannot reduce copies below currently active loans")
        
    book.title = req.title
    book.author = req.author
    book.isbn = req.isbn
    book.genre = req.genre
    book.publisher = req.publisher
    book.year = req.year
    book.copies = req.copies
    book.available_copies = new_available
    book.shelf_location = req.shelf_location
    book.rating = req.rating or 4.0
    book.description = req.description
    book.tags = req.tags
    
    db.commit()
    return {"ok": True, "message": "Book updated successfully"}

@router.delete("/books/{id}")
def delete_book(id: int, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"ok": True, "message": "Book deleted successfully"}
