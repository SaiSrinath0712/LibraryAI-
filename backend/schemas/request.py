from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RequestCreate(BaseModel):
    book_id: int
    member_id: str
    member_name: str
    department: Optional[str] = None
    preferred_date: Optional[str] = None
    note: Optional[str] = None

class RequestApproveReject(BaseModel):
    admin_note: Optional[str] = None
    due_date: Optional[str] = None

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
