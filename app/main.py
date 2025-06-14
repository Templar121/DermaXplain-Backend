from fastapi import FastAPI
from .routes import users, health, admin, scan

app = FastAPI()

# Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"]) 
app.include_router(scan.router, prefix="/scan", tags=["Scan"])
