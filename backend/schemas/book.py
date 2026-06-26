from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any
from datetime import datetime
import re

class BookBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, pattern=r"^[A-Za-z0-9 \-':,\.]+$")
    author: str = Field(..., min_length=3, max_length=100, pattern=r"^[A-Za-z \.']+$")
    isbn: Optional[str] = Field(None, pattern=r"^[\d\-]+$")
    genre: str = Field(..., min_length=2)
    publisher: Optional[str] = Field(None, pattern=r"^[A-Za-z0-9 &*\.,]+$")
    year: Optional[int] = None
    copies: int = Field(1, ge=1, le=1000)
    shelf_location: Optional[str] = Field(None, pattern=r"^[A-Z0-9\-]+$")
    shelf: Optional[str] = None
    rating: Optional[float] = Field(4.0, ge=1.0, le=5.0)
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[str] = Field(None, pattern=r"^[A-Za-z0-9, ]*$")

    @field_validator("title", "description", "tags")
    def sanitize_html(cls, v):
        if v:
            if "<script>" in v.lower() or "javascript:" in v.lower() or "drop table" in v.lower():
                raise ValueError("Malicious content detected")
            v = v.strip()
            v = re.sub(r'\s+', ' ', v)
        return v

    @field_validator("year", mode="before")
    def normalize_year(cls, v: Any):
        if v is None or v == "":
            return None
        year_val = int(v)
        if year_val < 1900 or year_val > datetime.now().year:
            raise ValueError(f"Year must be between 1900 and {datetime.now().year}")
        return year_val

    @model_validator(mode="after")
    def merge_shelf(self):
        if not self.shelf_location and self.shelf:
            if not re.match(r"^[A-Z0-9\-]+$", self.shelf):
                raise ValueError("Invalid shelf location format")
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
