from sqlalchemy.orm import Session
from models.book import Book
from models.loan import Loan
from typing import List

def recommend_books(db: Session, user_id: int, limit: int = 5) -> List[Book]:
    user_loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    
    # If the user has no loan history, return the most popular/top-rated books overall
    if not user_loans:
        return db.query(Book).order_by(Book.rating.desc(), Book.copies.desc()).limit(limit).all()
    
    genre_counts = {}
    borrowed_book_ids = set()
    for loan in user_loans:
        borrowed_book_ids.add(loan.book_id)
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        if book:
            genre_counts[book.genre] = genre_counts.get(book.genre, 0) + 1
            
    # Sort genres by preference
    fav_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    fav_genre_names = [g[0] for g in fav_genres]
    
    recommendations = []
    if fav_genre_names:
        recommendations = db.query(Book).filter(
            Book.genre.in_(fav_genre_names),
            ~Book.id.in_(borrowed_book_ids)
        ).order_by(Book.rating.desc()).limit(limit).all()
        
    # Pad with other highly-rated books if limit is not met
    if len(recommendations) < limit:
        pad_limit = limit - len(recommendations)
        already_recommended = [b.id for b in recommendations] + list(borrowed_book_ids)
        popular_books = db.query(Book).filter(
            ~Book.id.in_(already_recommended)
        ).order_by(Book.rating.desc()).limit(pad_limit).all()
        recommendations.extend(popular_books)
        
    return recommendations[:limit]
