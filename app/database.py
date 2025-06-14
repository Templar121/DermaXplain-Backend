import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Load the MongoDB connection string from the .env file
MONGO_URL = os.getenv("MONGO_URL")

# Create a Motor client instance
client = AsyncIOMotorClient(MONGO_URL)

# Access the database (you can rename "your_db_name" accordingly)
db = client["DermaXplain"]

# Optional: expose collections
users_collection = db["users"]
auth_collection = db["auth"]
scans_collection = db["scans"]
# Add more collections as needed
