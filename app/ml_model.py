from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError
import tensorflow as tf
from tensorflow.keras.models import load_model

# --- Label Mapping ---
label_mapping = {
    0: 'nv', 1: 'mel', 2: 'bkl', 3: 'bcc',
    4: 'akiec', 5: 'vasc', 6: 'df'
}
reverse_label_mapping = {v: k for k, v in label_mapping.items()}

# --- Resolve Model Path ---
# __file__ → .../DermaXplain-Backend/app/routes/ml_model.py
ROUTES_DIR = Path(__file__).resolve().parent          # .../app/routes
# APP_DIR    = ROUTES_DIR.parent                         # .../app
MODEL_PATH = ROUTES_DIR / "model" / "best_model.keras"  # adjust extension if needed

if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Model not found at {MODEL_PATH!r}")

# --- Load Keras Model ---
model = load_model(str(MODEL_PATH), compile=False)
print(f"[INFO] Loaded Keras model from {MODEL_PATH}")

# --- Preprocessing Function ---
def preprocess_image(image_path, target_size=(64, 64)):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {image_path}")
    except UnidentifiedImageError:
        print(f"[ERROR] Cannot identify image file: {image_path}")
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {e}")

    return None

# --- Prediction Function ---
def predict_scan(image_path: str):
    img_tensor = preprocess_image(image_path)
    if img_tensor is None:
        return "Unknown", 0.0

    try:
        preds = model.predict(img_tensor)
        pred_idx = int(np.argmax(preds, axis=1)[0])
        confidence = round(float(np.max(preds)), 4)
        label = label_mapping.get(pred_idx, 'Unknown')
        return label, confidence
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        return "Error", 0.0
