from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from ..auth import get_current_user
from ..database import scans_collection
from ..ml_model import predict_scan
from ..schemas import ScanOut
from typing import List
from bson import ObjectId, Binary
from datetime import datetime
import uuid, os, base64
from fastapi.responses import FileResponse
from app.utils.pdf_generator import generate_pdf_report
import asyncio
from app.utils.thread_executor import run_in_thread
import aiohttp
from dotenv import load_dotenv

load_dotenv()

EXPLAIN_SERVICE_URL = os.getenv(
    "EXPLAIN_MICROSERVICE_URL",
    "http://localhost:8001/explain"  # fallback
)

router = APIRouter()

readable_class_mapping = {
    "nv": "Melanocytic Nevi",
    "mel": "Melanoma",
    "bkl": "Benign Keratosis-like Lesions",
    "bcc": "Basal Cell Carcinoma",
    "akiec": "Actinic Keratoses",
    "vasc": "Vascular Lesions",
    "df": "Dermatofibroma"
}

# directory for temporary files
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def _background_explain_and_update(scan_id: str, image_path: str):
    # 1. Call the explanation microservice and get base64 strings
    result = await call_explanation_microservice(image_path)

    shap_b64 = result.get("shap_base64")
    occ_b64  = result.get("occlusion_base64")

    # 2. Update MongoDB directly with those base64 values
    await scans_collection.update_one(
        {"_id": ObjectId(scan_id)},
        {"$set": {
            "explanations.shap_base64": shap_b64,
            "explanations.occlusion_base64": occ_b64
        }}
    )

    # 3. Cleanup the temp image file
    try:
        os.remove(image_path)
    except OSError:
        pass

            
async def call_explanation_microservice(image_path: str):
    url = EXPLAIN_SERVICE_URL  # adjust if deployed differently
    try:
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as f:
                form = aiohttp.FormData()
                form.add_field('file', f, filename="scan.jpg", content_type='image/jpeg')

                async with session.post(url, data=form) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"[ERROR] Microservice failed: {resp.status}")
                        return {}
    except Exception as e:
        print(f"[ERROR] Could not contact microservice: {e}")
        return {}

@router.post("/upload-scan", response_model=ScanOut)
async def upload_scan(
    background_tasks: BackgroundTasks,
    patient_name: str = Form(...),
    patient_age: int = Form(...),
    gender: str = Form(...),
    scan_area: str = Form(...),
    additional_info: str = Form(""),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed.")

    # read and save image
    image_bytes = await image.read()
    temp_filename = f"{uuid.uuid4().hex}_{image.filename}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    # make prediction
    prediction_class, confidence_score = predict_scan(temp_path)

    # prepare initial document (explanations pending)
    scan_doc = {
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
        "prediction": {"class": prediction_class, "confidence": confidence_score},
        "explanations": {"shap_base64": None, "occlusion_base64": None}
    }
    result = await scans_collection.insert_one(scan_doc)
    scan_id = str(result.inserted_id)

    # schedule explanation in background
    background_tasks.add_task(_background_explain_and_update, scan_id, temp_path)

    # return initial response with image data
    return ScanOut(**{
        **scan_doc,
        "_id": scan_id,
        "image_base64": base64.b64encode(image_bytes).decode()
    })

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
                "confidence": doc.get("prediction", {}).get("confidence", 0.0)
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

    # base64 encode image and prepare explanations
    raw = doc.get("image_data")
    image_b64 = None
    if raw:
        image_bytes = raw if isinstance(raw, (bytes, bytearray)) else raw.value
        image_b64 = base64.b64encode(image_bytes).decode()

    explanations = doc.get("explanations", {})

    return ScanOut(**{
        **{k: v for k, v in doc.items() if k not in ["image_data", "_id"]},
        "_id": str(doc["_id"]),  # <-- ✅ ensure it's a string
        "image_base64": image_b64,
        "explanations": {
            "shap_base64": explanations.get("shap_base64"),
            "occlusion_base64": explanations.get("occlusion_base64")
        }
    })

@router.delete("/my-scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(scan_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    result = await scans_collection.delete_one({
        "_id": ObjectId(scan_id),
        "user_email": current_user["email"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found or unauthorized")

@router.get("/my-scans/{scan_id}/download")
async def download_scan_pdf(scan_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(scan_id):
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    doc = await scans_collection.find_one({
        "_id": ObjectId(scan_id),
        "user_email": user["email"]
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")

    # prepare data for PDF
    raw = doc.get("image_data")
    image_bytes = raw if isinstance(raw, (bytes, bytearray)) else raw.value
    doc["image_base64"] = base64.b64encode(image_bytes).decode()
    class_code = doc.get("prediction", {}).get("class", "")
    doc["prediction"]["readable_name"] = readable_class_mapping.get(class_code, "Unknown")
    doc["explanations"] = doc.get("explanations", {"shap_base64": None, "occlusion_base64": None})

    # generate PDF synchronously (fast) and schedule cleanup
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    pdf_path = os.path.join(UPLOAD_DIR, f"report_{scan_id}.pdf")
    generate_pdf_report(user, doc, pdf_path)

    async def _cleanup_pdf():
        await asyncio.sleep(10)
        try:
            os.remove(pdf_path)
        except OSError:
            pass
    asyncio.create_task(_cleanup_pdf())

    return FileResponse(
        path=pdf_path,
        filename=f"DermaXplain_Report_{scan_id}.pdf",
        media_type="application/pdf"
    )
