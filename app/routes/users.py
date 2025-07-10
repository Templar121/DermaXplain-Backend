from fastapi import APIRouter, HTTPException, status, Depends, Body
from .. import schemas, auth, email
from ..schemas import ForgotPasswordRequest
from ..database import users_collection, scans_collection
from ..auth import get_current_user
from bson import ObjectId
from passlib.context import CryptContext
import secrets
import os
from datetime import datetime, timedelta

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Register ---------------- #
@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)

    new_user = {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "hashed_password": hashed_password
    }

    result = await users_collection.insert_one(new_user)
    created_user = await users_collection.find_one({"_id": result.inserted_id})

    email.send_registration_email(to_email=created_user["email"], name=created_user["name"])
    return schemas.UserOut(**created_user)


# ---------------- Login ---------------- #
@router.post("/login", response_model=schemas.Token)
async def login(payload: schemas.LoginRequest):
    user = await auth.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = auth.create_access_token(data={"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


# ---------------- Get Logged-In User ---------------- #
@router.get("/me", response_model=schemas.UserOut)
async def get_user_me(current_user: dict = Depends(get_current_user)):
    return schemas.UserOut(**current_user)


# ---------------- Delete Account ---------------- #
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: dict = Depends(get_current_user)):
    result = await users_collection.delete_one({"email": current_user["email"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    await scans_collection.delete_many({"user_email": current_user["email"]})
    email.send_deletion_email(to_email=current_user["email"], name=current_user["name"])
    return None


# ---------------- Forgot Password ---------------- #
@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    user = await users_collection.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = secrets.token_urlsafe(32)
    
    # Optional: Set expiry
    # expiry = datetime.utcnow() + timedelta(minutes=15)
    
    await users_collection.update_one(
        {"email": payload.email},
        {"$set": {
            "reset_token": reset_token,
            # "reset_token_expiry": expiry
        }}
    )

    frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    await email.send_reset_email(to_email=payload.email, link=reset_link)

    return {"msg": "Password reset link sent"}


# ---------------- Reset Password ---------------- #
@router.post("/reset-password")
async def reset_password(token: str = Body(...), new_password: str = Body(...)):
    user = await users_collection.find_one({"reset_token": token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Optional: Check expiry
    # if "reset_token_expiry" in user and user["reset_token_expiry"] < datetime.utcnow():
    #     raise HTTPException(status_code=400, detail="Token expired")

    hashed = pwd_context.hash(new_password)

    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": hashed}, "$unset": {"reset_token": ""}}  # Also remove expiry if added
    )

    return {"message": "Password reset successfully"}


# ---------------- Update Username ---------------- #
@router.put("/update-username")
async def update_username(
    new_name: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    if not new_name.strip() or len(new_name.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

    await users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"name": new_name.strip()}}
    )

    return {"message": "Username updated successfully"}
