from pydantic import BaseModel, Field
from typing import Optional

class LoanIssueRequest(BaseModel):
    book_id: int = Field(..., gt=0)
    member_id: str = Field(..., pattern=r"^STU-\d{3}$")
    due_date: Optional[str] = None

class LoanRenewReturnRequest(BaseModel):
    loan_id: Optional[int] = None

class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: str
    due_date: str
    return_date: Optional[str] = None
    renew_count: int
    renewals: int # Alias for frontend
    status: str
    fine_amount: float
    fine: float # Alias for frontend
    request_id: Optional[int] = None

    book_title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    shelf: Optional[str] = None
    isbn: Optional[str] = None
    member_name: Optional[str] = None
    member_id: Optional[str] = None
    department: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
