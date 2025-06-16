from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from ..auth import get_current_user
from ..database import scans_collection
from ..ml_model import predict_scan
from ..schemas import ScanOut
from typing import List
from bson import ObjectId
from datetime import datetime
import uuid, shutil, os

router = APIRouter()

UPLOAD_DIR = "uploaded_scans"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-scan", response_model=ScanOut)
async def upload_scan(
    patient_name: str = Form(...),
    patient_age: int = Form(...),
    gender: str = Form(...),
    scan_area: str = Form(...),
    additional_info: str = Form(""),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed.")

    filename = f"{uuid.uuid4().hex}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # ML prediction
    prediction_class, confidence_score = predict_scan(file_path)

    # Build scan document
    scan = {
        "user_email": current_user["email"],
        "patient_name": patient_name,
        "patient_age": patient_age,
        "gender": gender,
        "scan_area": scan_area,
        "additional_info": additional_info,
        "uploaded_at": datetime.utcnow(),
        "image_path": file_path,
        "image_filename": filename,
        "prediction": {
            "class": prediction_class,
            "confidence": confidence_score
        }
    }

    result = await scans_collection.insert_one(scan)
    scan["_id"] = str(result.inserted_id)

    return ScanOut(**scan)


@router.get("/my-scans", response_model=List[ScanOut])
async def get_user_scans(current_user: dict = Depends(get_current_user)):
    scans = []
    async for scan in scans_collection.find({"user_email": current_user["email"]}):
        scan["_id"] = str(scan["_id"])  # Convert ObjectId to str
        scans.append(ScanOut(**scan))
    return scans
