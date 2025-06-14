from fastapi import APIRouter, Depends, HTTPException
from ..schemas import ScanCreate, ScanOut
from ..auth import get_current_user
from ..database import scans_collection
from typing import List
from bson import ObjectId

router = APIRouter()

@router.post("/upload-scan", response_model=ScanOut)
async def upload_scan(data: ScanCreate, current_user: dict = Depends(get_current_user)):
    scan = {
        "user_email": current_user["email"],  # <-- Important for tracking user-specific scans
        "patient_name": data.patient_name,
        "patient_age": data.patient_age,
        "gender": data.gender,
        "scan_area": data.scan_area,
        "additional_info": data.additional_info
    }

    result = await scans_collection.insert_one(scan)
    scan["_id"] = result.inserted_id # Add inserted ID to return it in ScanOut
    scan["_id"] = str(scan["_id"])
    return ScanOut(**scan)


@router.get("/my-scans", response_model=List[ScanOut])
async def get_user_scans(current_user: dict = Depends(get_current_user)):
    scans = []
    async for scan in scans_collection.find({"user_email": current_user["email"]}):
        scan["_id"] = str(scan["_id"])  # ✅ Convert ObjectId to str
        scans.append(ScanOut(**scan))
    return scans


