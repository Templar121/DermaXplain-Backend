from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from ..database import users_collection, scans_collection
from ..auth import get_current_user
from ..schemas import UserOut
from .. import email

router = APIRouter()

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user

@router.get("/users", response_model=List[UserOut], tags=["Admin"])
async def list_all_users(admin: dict = Depends(require_admin)):
    users = []
    async for user in users_collection.find():
        users.append(UserOut(**user))
    return users

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin"]
)
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    # 1) Validate the ID format
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # 2) Fetch user
    obj_id = ObjectId(user_id)
    user = await users_collection.find_one({"_id": obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3) Delete user
    await users_collection.delete_one({"_id": obj_id})

    # 4) Cascade delete scans
    result = await scans_collection.delete_many({"user_email": user["email"]})
    # (OPTIONAL) You could log result.deleted_count here

    # 5) Notify the user
    email.send_admin_deletion_email(to_email=user["email"], name=user["name"])

    # 6) Return 204 No Content
    return None
