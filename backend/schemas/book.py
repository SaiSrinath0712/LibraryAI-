from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    publisher: Optional[str] = None
    year: Optional[int] = None
    copies: int = Field(1, gt=0)
    shelf_location: Optional[str] = None
    shelf: Optional[str] = None
    rating: Optional[float] = Field(4.0, ge=1.0, le=5.0)
    description: Optional[str] = None
    tags: Optional[str] = None

    @field_validator("year", mode="before")
    @classmethod
    def normalize_year(cls, v: Any):
        if v is None or v == "":
            return None
        return int(v)

    @model_validator(mode="after")
    def merge_shelf(self):
        if not self.shelf_location and self.shelf:
            self.shelf_location = self.shelf
        return self

class BookCreate(BookBase):
    pass

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    publisher: Optional[str] = None
    year: Optional[int] = None
    copies: int
    available_copies: int
    available: int
    shelf_location: Optional[str] = None
    shelf: Optional[str] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    borrow_count: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
