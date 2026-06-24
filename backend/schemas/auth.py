import re
from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    member_id: Optional[str] = None
    username: Optional[str] = None
    password: str

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    member_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    password: str = Field(..., min_length=6)

class ChangePasswordRequest(BaseModel):
    username: Optional[str] = None
    member_id: Optional[str] = None
    current_password: str
    new_password: str
