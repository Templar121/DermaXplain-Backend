from fastapi import FastAPI
from .routes import users, health

app = FastAPI()

# Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# If you later add an admin route:
# app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
