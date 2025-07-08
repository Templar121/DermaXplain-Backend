from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from ..auth import get_current_user
from ..database import scans_collection
from ..ml_model import predict_scan
from ..schemas import ScanOut
from typing import List
from bson import ObjectId, Binary
from datetime import datetime
import uuid, shutil, os, base64

router = APIRouter()

UPLOAD_DIR = "temp_uploads"
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

    image_bytes = await image.read()

    # Save temp file for prediction
    temp_filename = f"{uuid.uuid4().hex}_{image.filename}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    prediction_class, confidence_score = predict_scan(temp_path)
    os.remove(temp_path)

    scan = {
        "user_email": current_user["email"],
        "patient_name": patient_name,
        "patient_age": patient_age,
        "gender": gender,
        "scan_area": scan_area,
        "additional_info": additional_info,
        "uploaded_at": datetime.utcnow(),
        "image_data": Binary(image_bytes),
        "image_filename": image.filename,
        "image_content_type": image.content_type,
        "prediction": {
            "class": prediction_class,
            "confidence": confidence_score
        }
    }

    result = await scans_collection.insert_one(scan)

    # ← Here’s the crucial line:
    scan["_id"] = str(result.inserted_id)

    scan["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")

    return ScanOut(**scan)



@router.get("/my-scans", response_model=List[dict])
async def get_user_scans(current_user: dict = Depends(get_current_user)):
    scans = []
    cursor = scans_collection.find({"user_email": current_user["email"]})
    async for doc in cursor:
        scans.append({
            "_id": str(doc["_id"]),
            "patient_name": doc.get("patient_name", "N/A"),
            "prediction": {
                "class": doc.get("prediction", {}).get("class", "N/A"),
                "confidence": doc.get("prediction", {}).get("confidence", 0.0),
            }
        })
    return scans

@router.get("/my-scans/{scan_id}", response_model=ScanOut)
async def get_scan_detail(scan_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    doc = await scans_collection.find_one({
        "_id": ObjectId(scan_id),
        "user_email": current_user["email"]
    })

    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Convert MongoDB _id to string
    doc["_id"] = str(doc["_id"])

    # Convert Binary to base64
    raw = doc.get("image_data")
    if raw:
        image_bytes = raw if isinstance(raw, (bytes, bytearray)) else raw.value
        doc["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")
    else:
        doc["image_base64"] = None

    # Remove image_data so it doesn't interfere with Pydantic
    doc.pop("image_data", None)

    return ScanOut(**doc)

@router.delete("/my-scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(scan_id: str, current_user: dict = Depends(get_current_user)):
    print(f"Authenticated user: {current_user['email']}")

    if not ObjectId.is_valid(scan_id):
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    result = await scans_collection.delete_one({
        "_id": ObjectId(scan_id),
        "user_email": current_user["email"]  # 🔐 ensures only the owner can delete
    })

    print(f"Deleted count: {result.deleted_count}")

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Scan not found or you do not have permission to delete it"
        )