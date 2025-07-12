from PIL import Image as PILImage
PILImage._showxv = lambda *args, **kwargs: None  # disables internal GUI calls
PILImage.show = lambda *args, **kwargs: None

from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError
import tensorflow as tf
from tensorflow.keras.models import load_model
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# --- Label Mapping ---
label_mapping = {
    0: 'nv', 1: 'mel', 2: 'bkl', 3: 'bcc',
    4: 'akiec', 5: 'vasc', 6: 'df'
}
reverse_label_mapping = {v: k for k, v in label_mapping.items()}
class_names = [label_mapping[i] for i in sorted(label_mapping.keys())]

# --- Load Keras Model Once ---
ROUTES_DIR = Path(__file__).resolve().parent
MODEL_PATH = ROUTES_DIR / "model" / "best_model.keras"

if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Model not found at {MODEL_PATH!r}")

model = load_model(str(MODEL_PATH), compile=False)
print(f"[INFO] Loaded model from {MODEL_PATH}")

# --- Fast Preprocessing ---
def preprocess_image(image_path, target_size=(64, 64)):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        arr = np.asarray(img, dtype=np.float32)
        return np.expand_dims(arr, axis=0)  # (1, 64, 64, 3)
    except (FileNotFoundError, UnidentifiedImageError):
        print(f"[ERROR] Invalid image: {image_path}")
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {e}")
    return None

# --- Core Fast Prediction ---
def predict_scan(image_path: str):
    img_tensor = preprocess_image(image_path)
    if img_tensor is None:
        return "Unknown", 0.0

    try:
        preds = model.predict(img_tensor, verbose=0)
        pred_idx = int(np.argmax(preds[0]))
        confidence = round(float(np.max(preds[0])), 4)
        label = label_mapping.get(pred_idx, 'Unknown')
        return label, confidence
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        return "Error", 0.0
