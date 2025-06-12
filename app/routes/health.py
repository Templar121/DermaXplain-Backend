from fastapi import APIRouter
from app.database import db

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "API is healthy ✅"}

@router.get("/db")
async def health_check():
    try:
        # MongoDB ping to check connection
        await db.command("ping")
        return {"status": "✅ API is healthy and MongoDB connection successful!"}
    except Exception as e:
        return {
            "status": "❌ API is running but MongoDB connection failed!",
            "error": str(e)
        }