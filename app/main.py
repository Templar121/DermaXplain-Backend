# app/main.py
from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS as before…
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# placeholder for model & explainer
@app.on_event("startup")
def setup_model():
    import tensorflow as tf
    from tensorflow.keras.models import load_model

    # Resolve the path to the model folder next to main.py
    BASE_DIR  = Path(__file__).resolve().parent
    MODEL_DIR = BASE_DIR.parent / "app" / "model"
    MODEL_PATH = MODEL_DIR / "best_model.keras"

    if not MODEL_PATH.is_file():
        raise RuntimeError(f"Model not found at {MODEL_PATH!r}")

    app.state.model = load_model(str(MODEL_PATH), compile=False)
    print(f"[INFO] Model loaded at startup from {MODEL_PATH}")

# include your routers
from .routes import health, users, admin, scan, google_auth
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(scan.router, prefix="/scan", tags=["Scan"])
app.include_router(google_auth.router)
