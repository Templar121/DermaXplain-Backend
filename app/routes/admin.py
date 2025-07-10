from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from ..database import users_collection, scans_collection
from ..auth import get_current_user
from ..schemas import UserOut
from .. import email
import base64
import os
from fastapi import Path

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

@router.get("/users/{user_id}/scans", tags=["Admin"])
async def get_scan_ids_by_user_id(
    user_id: str = Path(..., title="User ID"),
    admin: dict = Depends(require_admin)
):
    # Step 1: Validate user_id
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    obj_user_id = ObjectId(user_id)
    
    # Step 2: Get user
    user = await users_collection.find_one({"_id": obj_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_email = user["email"]

    # Step 3: Fetch scans using user_email
    scan_ids = []
    async for scan in scans_collection.find({"user_email": user_email}, {"_id": 1}):
        scan_ids.append(str(scan["_id"]))

    # Step 4: Return result
    return {
        "user_id": user_id,
        "scan_ids": scan_ids
    }


@router.get("/scans/{scan_id}", tags=["Admin"])
async def get_scan_by_scan_id(
    scan_id: str = Path(..., title="Scan ID"),
    admin: dict = Depends(require_admin)
):
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    scan = await scans_collection.find_one({"_id": ObjectId(scan_id)})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Convert _id and uploaded_at
    scan["_id"] = str(scan["_id"])
    if "uploaded_at" in scan and hasattr(scan["uploaded_at"], "isoformat"):
        scan["uploaded_at"] = scan["uploaded_at"].isoformat()

    # Handle image_data stored in DB
    raw = scan.get("image_data")
    if raw:
        image_bytes = raw if isinstance(raw, (bytes, bytearray)) else raw.value
        scan["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")
    else:
        scan["image_base64"] = None

    # Clean binary fields
    scan.pop("image_data", None)

    return scan
