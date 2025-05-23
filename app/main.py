from fastapi import FastAPI
from . import models, database
from .routes import users, health, admin

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])


app.include_router(admin.router)
