from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models.user import User
from schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest
from utils.security import get_password_hash, verify_password
from utils.jwt_handler import create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/auth/register")
@router.post("/student/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    exists_id = db.query(User).filter(User.member_id == req.member_id).first()
    if exists_id:
        raise HTTPException(status_code=409, detail="Member ID already exists")

    email = (req.email or "").strip() or f"{req.member_id.lower()}@library.local"
    exists_email = db.query(User).filter(User.email == email).first()
    if exists_email:
        raise HTTPException(status_code=409, detail="Email already exists")

    new_user = User(
        name=req.name,
        member_id=req.member_id,
        email=email,
        phone=(req.phone or "").strip() or None,
        department=req.department or None,
        year=req.year or None,
        password_hash=get_password_hash(req.password),
        role="student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"ok": True, "message": "User registered successfully"}

@router.post("/auth/login")
@router.post("/student/login")
@router.post("/admin/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = None
    if req.username:
        if req.username.strip().lower() != "admin":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = db.query(User).filter(User.role == "admin").first()
    elif req.member_id:
        # Student login
        user = db.query(User).filter(User.member_id == req.member_id).first()
    else:
        # Fallback to checking by username or email
        # If username is sent but not literal 'admin', check email or member_id
        user = db.query(User).filter(User.email == req.username).first()
        if not user:
            user = db.query(User).filter(User.member_id == req.username).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    if user.role == "admin":
        return {
            "ok": True, 
            "access_token": token, 
            "token_type": "bearer",
            "admin": {"id": user.id, "name": user.name, "username": "admin"}
        }
    else:
        return {
            "ok": True, 
            "access_token": token, 
            "token_type": "bearer",
            "student": {
                "id": user.id, 
                "name": user.name, 
                "member_id": user.member_id,
                "email": user.email,
                "phone": user.phone,
                "department": user.department,
                "year": user.year
            }
        }

@router.post("/auth/change-password")
@router.post("/admin/change-password")
def change_password(req: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = None
    # Support checking admin password change or student password change
    if req.username:
        user = db.query(User).filter(User.role == "admin").first()
    elif req.member_id:
        user = db.query(User).filter(User.member_id == req.member_id).first()
    
    if not user or not verify_password(req.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password incorrect")
        
    user.password_hash = get_password_hash(req.new_password)
    db.commit()
    return {"ok": True, "message": "Password updated successfully"}
