from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema
from datetime import datetime
from typing import Optional, Dict

# ✅ Pydantic v2 compatible ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.any_schema()
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


# ✅ Schema for user registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "user"  # defaults to "user"


# ✅ Schema for user response (e.g., /register, /me, admin)
class UserOut(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    email: EmailStr
    name: str
    role: Optional[str] = "user"

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True


# ✅ Token schema
class Token(BaseModel):
    access_token: str
    token_type: str


# ✅ Token data for internal use
class TokenData(BaseModel):
    email: Optional[str] = None


# ✅ Login request body
class LoginRequest(BaseModel):
    email: str
    password: str

class ScanCreate(BaseModel):
    patient_name: str
    patient_age: int
    gender: str
    scan_area: str
    additional_info: Optional[str] = None

class Prediction(BaseModel):
    class_: str          = Field(alias="class")
    confidence: float

    class Config:
        populate_by_name = True
        
class ScanOut(BaseModel):
    id: str = Field(alias="_id")
    patient_name: str
    patient_age: int
    gender: str
    scan_area: str
    additional_info: Optional[str]
    uploaded_at: datetime
    image_filename: str
    prediction: Prediction  # or Dict[str, float]
    image_base64: Optional[str]

    class Config:
        from_attributes      = True
        json_encoders        = {ObjectId: str}
        populate_by_name     = True
        arbitrary_types_allowed = True
        
class ForgotPasswordRequest(BaseModel):
    email: EmailStr