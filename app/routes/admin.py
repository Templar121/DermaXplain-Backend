from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..database import users_collection, scans_collection
from ..auth import get_current_user
from ..schemas import UserOut
from .. import email
from bson import ObjectId

router = APIRouter()

# Dependency to verify admin access
async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only")
    return current_user

# Get all users
@router.get("/users", response_model=List[UserOut])
async def list_all_users(admin: dict = Depends(require_admin)):
    users = []
    async for user in users_collection.find():
        users.append(UserOut(**user))
    return users

# Delete a user by ID
@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    await users_collection.delete_one({"_id": ObjectId(user_id)})

    # Delete all scans of that user
    await scans_collection.delete_many({"user_email": user["email"]})

    # Send admin-triggered deletion email
    email.send_admin_deletion_email(to_email=user["email"], name=user["name"])

    return None
