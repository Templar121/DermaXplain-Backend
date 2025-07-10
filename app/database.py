import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from dotenv import load_dotenv
import certifi
import gridfs

load_dotenv()

# Load the MongoDB connection string from the .env file
MONGO_URL = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(
    MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000,
)

# Access the database (you can rename "your_db_name" accordingly)
db = client["DermaXplain"]

fs_bucket = AsyncIOMotorGridFSBucket(db)

# Optional: expose collections
users_collection = db["users"]
auth_collection = db["auth"]
scans_collection = db["scans"]
# Add more collections as needed
