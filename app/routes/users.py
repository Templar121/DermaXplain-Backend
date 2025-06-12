from fastapi import APIRouter, HTTPException, status, Depends
from .. import schemas, auth, email
from ..database import db, users_collection
from ..auth import get_current_user
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    
    new_user = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password
    }
    
    result = await users_collection.insert_one(new_user)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    # Send email (assumes email.send_registration_email is async-safe or fire-and-forget)
    email.send_registration_email(to_email=created_user["email"], name=created_user["name"])

    # Respond with user info (MongoDB _id will be used via schemas.UserOut)
    return schemas.UserOut(**created_user)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: dict = Depends(get_current_user)):
    result = await users_collection.delete_one({"email": current_user["email"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found or already deleted")
    
    # ✅ Send deletion confirmation email
    email.send_deletion_email(to_email=current_user["email"], name=current_user["name"])

    return {"Successfully Deleted"}

@router.post("/login", response_model=schemas.Token)
async def login(payload: schemas.LoginRequest):
    user = await auth.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    token = auth.create_access_token(data={"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_user_me(current_user: dict = Depends(auth.get_current_user)):
    return {"email": current_user["email"]}
