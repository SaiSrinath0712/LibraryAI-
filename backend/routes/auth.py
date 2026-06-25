from fastapi import APIRouter, Depends, HTTPException, status
from database.db import get_db, get_next_sequence_value
from schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest
from utils.security import get_password_hash, verify_password
from utils.jwt_handler import create_access_token
from datetime import datetime

router = APIRouter(tags=["Authentication"])

@router.post("/auth/register")
@router.post("/student/register")
def register(req: RegisterRequest, db=Depends(get_db)):
    exists_id = db.users.find_one({"member_id": req.member_id})
    if exists_id:
        raise HTTPException(status_code=409, detail="Member ID already exists")

    email = (req.email or "").strip() or f"{req.member_id.lower()}@library.local"
    exists_email = db.users.find_one({"email": email})
    if exists_email:
        raise HTTPException(status_code=409, detail="Email already exists")

    new_id = get_next_sequence_value("userid")
    new_user = {
        "id": new_id,
        "name": req.name,
        "member_id": req.member_id,
        "email": email,
        "phone": (req.phone or "").strip() or None,
        "department": req.department or None,
        "year": req.year or None,
        "password_hash": get_password_hash(req.password),
        "role": "student",
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(new_user)
    return {"ok": True, "message": "User registered successfully"}

@router.post("/auth/login")
@router.post("/student/login")
@router.post("/admin/login")
def login(req: LoginRequest, db=Depends(get_db)):
    user = None
    if req.username:
        if req.username.strip().lower() != "admin":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = db.users.find_one({"role": "admin"})
    elif req.member_id:
        user = db.users.find_one({"member_id": req.member_id})
    else:
        user = db.users.find_one({"email": req.username})
        if not user:
            user = db.users.find_one({"member_id": req.username})

    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    
    if user["role"] == "admin":
        return {
            "ok": True, 
            "access_token": token, 
            "token_type": "bearer",
            "admin": {"id": user["id"], "name": user["name"], "username": "admin"}
        }
    else:
        return {
            "ok": True, 
            "access_token": token, 
            "token_type": "bearer",
            "student": {
                "id": user["id"], 
                "name": user["name"], 
                "member_id": user["member_id"],
                "email": user["email"],
                "phone": user.get("phone"),
                "department": user.get("department"),
                "year": user.get("year")
            }
        }

@router.post("/auth/change-password")
@router.post("/admin/change-password")
def change_password(req: ChangePasswordRequest, db=Depends(get_db)):
    user = None
    if req.username:
        user = db.users.find_one({"role": "admin"})
    elif req.member_id:
        user = db.users.find_one({"member_id": req.member_id})
    
    if not user or not verify_password(req.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Current password incorrect")
        
    db.users.update_one({"_id": user["_id"]}, {"$set": {"password_hash": get_password_hash(req.new_password)}})
    return {"ok": True, "message": "Password updated successfully"}
