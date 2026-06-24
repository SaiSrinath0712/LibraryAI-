from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    member_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    role: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
