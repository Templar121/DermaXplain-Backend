from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError
import tensorflow as tf
from tensorflow.keras.models import load_model
import shap
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

# ===========================
# 🔍 Optional Explanations
# ===========================

# SHAP Explanation (only if needed)
def explain_with_shap(image_path: str, save_path: str):
    try:
        img = Image.open(image_path).convert('RGB').resize((64, 64))
        arr = np.asarray(img, dtype=np.float32)
        preds = model.predict(preprocess_image(image_path), verbose=0)[0]
        label = class_names[np.argmax(preds)]
        conf = float(np.max(preds))

        masker = shap.maskers.Image('inpaint_telea', arr.shape)
        def shap_predict(x):
            batch = np.stack([preprocess_image_from_array(im)[0] for im in x])
            return model.predict(batch, verbose=0)

        explainer = shap.Explainer(shap_predict, masker, output_names=class_names)
        explanation = explainer(arr[np.newaxis, ...], max_evals=50)
        shap_vals = explanation.values[0]

        top_cls = np.argsort(preds)[::-1][:2]
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        for ax, cls in zip(axes, top_cls):
            overlay = shap_vals[:, :, :, cls].mean(axis=-1)
            overlay -= overlay.mean()
            overlay /= (np.abs(overlay).max() + 1e-8)
            ax.imshow(arr.astype(np.uint8))
            ax.imshow(overlay, cmap='bwr', alpha=0.5, vmin=-1, vmax=1)
            ax.set_title(f"{class_names[cls]} ({preds[cls]:.2f})")
            ax.axis('off')
        plt.tight_layout()
        out_path = Path(save_path)
        out_path = out_path.with_name(out_path.stem + "_shap.png")
        plt.savefig(out_path)
        plt.close()
        return str(out_path)
    except Exception as e:
        print(f"[ERROR] SHAP explanation failed: {e}")
        return None

def preprocess_image_from_array(img_array):
    img = tf.image.resize(img_array, (64, 64)).numpy().astype(np.float32)
    return np.expand_dims(img, axis=0)

# Occlusion Map (lightweight, optional)
def explain_with_occlusion(image_path: str, save_path: str):
    try:
        img = Image.open(image_path).convert('RGB').resize((64, 64))
        arr = np.asarray(img, dtype=np.float32)
        input_tensor = preprocess_image_from_array(arr)
        preds = model.predict(input_tensor, verbose=0)[0]
        class_index = int(np.argmax(preds))
        confidence = preds[class_index]

        patch_size = 15
        stride = 8
        mean_pixel = np.mean(arr, axis=(0, 1), keepdims=True)
        heatmap = np.zeros((64, 64), dtype=np.float32)
        for y in range(0, 64 - patch_size + 1, stride):
            for x in range(0, 64 - patch_size + 1, stride):
                occluded = arr.copy()
                occluded[y:y+patch_size, x:x+patch_size] = mean_pixel
                pred = model.predict(preprocess_image_from_array(occluded), verbose=0)[0]
                drop = confidence - pred[class_index]
                heatmap[y:y+patch_size, x:x+patch_size] = drop

        # Normalize
        if heatmap.max() > heatmap.min():
            heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

        # Save
        out_path = Path(save_path)
        out_path = out_path.with_name(out_path.stem + "_occ.png")
        plt.imshow(arr.astype(np.uint8), alpha=0.6)
        plt.imshow(heatmap, cmap='jet', alpha=0.5)
        plt.colorbar()
        plt.title(f"Occlusion Map ({class_names[class_index]})")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        return str(out_path)
    except Exception as e:
        print(f"[ERROR] Occlusion explanation failed: {e}")
        return None

# Unified Explanation
def explain_image(image_path: str):
    shap_path = explain_with_shap(image_path, image_path)
    occ_path = explain_with_occlusion(image_path, image_path)
    return {
        "shap": shap_path,
        "occlusion": occ_path
    }
