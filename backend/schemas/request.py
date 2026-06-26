from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class RequestCreate(BaseModel):
    book_id: int = Field(..., gt=0)
    member_id: str = Field(..., pattern=r"^STU-\d{3}$")
    member_name: str = Field(..., min_length=3, max_length=50, pattern=r"^[A-Za-z ]+$")
    department: Optional[str] = None
    preferred_date: Optional[str] = None
    note: Optional[str] = Field(None, max_length=300)

    @field_validator("note")
    def sanitize_note(cls, v):
        if v:
            if "<script>" in v.lower() or "javascript:" in v.lower():
                raise ValueError("Malicious content detected")
            return v.strip()
        return v

class RequestApproveReject(BaseModel):
    admin_note: Optional[str] = Field(None, max_length=300)
    due_date: Optional[str] = None

    @field_validator("admin_note")
    def sanitize_note(cls, v):
        if v:
            if "<script>" in v.lower() or "javascript:" in v.lower():
                raise ValueError("Malicious content detected")
            return v.strip()
        return v

class RequestResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    request_date: datetime
    preferred_date: Optional[str] = None
    note: Optional[str] = None
    status: str
    admin_note: Optional[str] = None
    action_time: Optional[datetime] = None
    created_at: datetime
    
    book_title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    book_available: Optional[int] = None
    member_name: Optional[str] = None
    member_id: Optional[str] = None
    department: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
