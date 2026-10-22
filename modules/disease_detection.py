"""
Plant Disease Detection Module
Uses MobileNetV2 CNN model to detect diseases from leaf images.
Falls back to demo mode when model not available.
"""

import os
import json
import numpy as np
from datetime import datetime

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH    = os.path.join(BASE_DIR, "models", "disease_model.h5")
DISEASES_JSON = os.path.join(BASE_DIR, "data", "diseases.json")
HISTORY_JSON  = os.path.join(BASE_DIR, "data", "user_history.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "uploads")

IMG_SIZE    = 224
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def _load_diseases():
    with open(DISEASES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["diseases"], data["class_labels"]


def _save_history(entry: dict):
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["disease_detections"].append(entry)
    history["disease_detections"] = history["disease_detections"][-50:]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _preprocess_image(image_path: str):
    """Load and preprocess image for MobileNetV2."""
    from PIL import Image
    img = Image.open(image_path).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img, dtype=np.float32)
    arr = arr / 127.5 - 1.0          # MobileNetV2 preprocessing
    return np.expand_dims(arr, axis=0)


def detect_disease(image_path: str) -> dict:
    """
    Analyze leaf image and return disease diagnosis with treatment advice.
    """
    diseases, class_labels = _load_diseases()

    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    predicted_class = None
    confidence      = 0.0
    top_predictions = []

    model_available = os.path.exists(MODEL_PATH)

    if model_available:
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(MODEL_PATH)
            img_array = _preprocess_image(image_path)
            preds = model.predict(img_array, verbose=0)[0]

            top_idx  = np.argsort(preds)[::-1][:3]
            predicted_class = top_idx[0]
            confidence      = float(preds[top_idx[0]]) * 100

            top_predictions = [
                {"label": class_labels[i], "confidence": round(float(preds[i]) * 100, 1)}
                for i in top_idx
            ]
        except Exception as e:
            model_available = False

    if not model_available:
        # Demo mode: pick a random realistic disease for demonstration
        predicted_class = int(np.random.randint(0, len(diseases)))
        confidence      = round(np.random.uniform(72, 96), 1)
        top_predictions = [
            {"label": class_labels[predicted_class], "confidence": confidence},
            {"label": class_labels[(predicted_class + 1) % len(diseases)],
             "confidence": round(confidence * 0.4, 1)},
            {"label": class_labels[(predicted_class + 2) % len(diseases)],
             "confidence": round(confidence * 0.1, 1)},
        ]

    disease_info = diseases[predicted_class] if predicted_class < len(diseases) else diseases[0]

    is_healthy = disease_info.get("severity", "") == "None"

    result = {
        "success":         True,
        "disease_name":    disease_info["name"],
        "crop":            disease_info["crop"],
        "pathogen":        disease_info["pathogen"],
        "symptoms":        disease_info["symptoms"],
        "treatment":       disease_info["treatment"],
        "prevention":      disease_info["prevention"],
        "severity":        disease_info["severity"],
        "confidence":      round(confidence, 1),
        "is_healthy":      is_healthy,
        "icon":            disease_info.get("icon", "🌿"),
        "top_predictions": top_predictions,
        "model_used":      "CNN MobileNetV2" if model_available else "Demo Mode",
        "demo_notice":     "" if model_available else
                           "Running in demo mode. Train the model with PlantVillage dataset for real predictions."
    }

    _save_history({
        "timestamp":   datetime.now().isoformat(),
        "disease":     disease_info["name"],
        "confidence":  round(confidence, 1),
        "is_healthy":  is_healthy
    })

    return result
