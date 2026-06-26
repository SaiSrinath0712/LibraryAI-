import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class LoginRequest(BaseModel):
    member_id: Optional[str] = None
    username: Optional[str] = None
    password: str

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[A-Za-z ]+$")
    member_id: str = Field(..., pattern=r"^STU-\d{3}$")
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    department: Optional[str] = None
    year: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=50, pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$")

    @field_validator("name")
    def clean_name(cls, v):
        v = v.strip()
        v = re.sub(r'\s+', ' ', v)
        return v

class ChangePasswordRequest(BaseModel):
    username: Optional[str] = None
    member_id: Optional[str] = None
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=50, pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$")
