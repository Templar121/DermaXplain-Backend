from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.database import users_collection
from app.schemas import UserOut
import jwt
import os
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("SECRET_KEY", "secret_key")

class TokenModel(BaseModel):
    token: str

@router.post("/auth/google")
async def google_login(data: TokenModel):
    try:
        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(
            data.token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]
        name = idinfo.get("name", email.split("@")[0])

        user = await users_collection.find_one({"email": email})
        if not user:
            user_data = {"name": name, "email": email, "role": "user"}
            result = await users_collection.insert_one(user_data)
            user = user_data
            user["_id"] = result.inserted_id

        payload = {
            "sub": str(user["email"]),
            "email": user["email"],
            "role": user.get("role", "user")
        }
        access_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user.get("role", "user")
            }
        }

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
