from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import users, health, admin, scan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # or restrict to ["http://localhost:3000"] etc.
    allow_credentials=True,
    allow_methods=["*"],            # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],            # allow Authorization header, Content-Type, etc.
)

# Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"]) 
app.include_router(scan.router, prefix="/scan", tags=["Scan"])
