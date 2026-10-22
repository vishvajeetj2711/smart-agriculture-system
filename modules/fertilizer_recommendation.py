"""
Fertilizer Recommendation Module
Uses a trained Random Forest classifier to recommend the best
fertilizer based on soil nutrients and crop type.
"""

import os
import json
import numpy as np
from datetime import datetime

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH      = os.path.join(BASE_DIR, "models", "fertilizer_model.pkl")
FERT_JSON       = os.path.join(BASE_DIR, "data", "fertilizers.json")
HISTORY_JSON    = os.path.join(BASE_DIR, "data", "user_history.json")

CROP_ENC = {
    "Rice": 0, "Wheat": 1, "Maize": 2, "Cotton": 3, "Sugarcane": 4,
    "Soybean": 5, "Tomato": 6, "Onion": 7, "Groundnut": 8, "Mango": 9,
    "Potato": 6, "Vegetables": 6, "Other": 1
}


def _load_fertilizers():
    with open(FERT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)["fertilizers"]


def _save_history(entry: dict):
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["fertilizer_recommendations"].append(entry)
    history["fertilizer_recommendations"] = history["fertilizer_recommendations"][-50:]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _rule_based_recommend(soil_N: float, soil_P: float, soil_K: float,
                           ph: float, crop: str, moisture: float,
                           fertilizers: list) -> list:
    """Rule-based fallback when model file is absent."""
    scores = []
    crop_lower = crop.lower()

    for fert in fertilizers:
        score = 0
        # Check if crop matches
        for c in fert.get("best_for_crops", []):
            if c.lower() == crop_lower or c == "All crops":
                score += 30
                break

        # Nitrogen deficiency
        if soil_N < 50:
            if "Nitrogen" in fert.get("nutrient_provided", ""):
                score += 25
        elif soil_N > 100:
            if "Organic" in fert.get("type", ""):
                score += 10

        # Phosphorus deficiency
        if soil_P < 30:
            if "Phosphorus" in fert.get("nutrient_provided", ""):
                score += 20

        # Potassium deficiency
        if soil_K < 30:
            if "Potassium" in fert.get("nutrient_provided", ""):
                score += 20

        # pH adjustment
        if ph < 6.0:
            if fert["name"] in ["SSP (Single Super Phosphate)"]:
                score += 10

        scores.append((fert, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [f for f, _ in scores[:3]]


def get_recommendation(soil_N: float, soil_P: float, soil_K: float,
                       ph: float, crop: str, moisture: float = 50.0) -> dict:
    """
    Returns top 3 fertilizer recommendations with application details.
    Features: [N, P, K, ph, crop_enc, moisture]
    """
    fertilizers = _load_fertilizers()
    model_available = os.path.exists(MODEL_PATH)

    top_fertilizers = []

    if model_available:
        try:
            import joblib
            model = joblib.load(MODEL_PATH)
            crop_enc = CROP_ENC.get(crop, 1)
            features = np.array([[soil_N, soil_P, soil_K, ph, crop_enc, moisture]])
            proba    = model.predict_proba(features)[0]
            top_idx  = np.argsort(proba)[::-1][:3]
            classes  = model.classes_

            for idx in top_idx:
                fert_id = int(classes[idx])
                conf    = float(proba[idx]) * 100
                if fert_id < len(fertilizers):
                    f = fertilizers[fert_id].copy()
                    f["confidence"] = round(conf, 1)
                    top_fertilizers.append(f)
        except Exception:
            model_available = False

    if not model_available or not top_fertilizers:
        top_fertilizers = _rule_based_recommend(
            soil_N, soil_P, soil_K, ph, crop, moisture, fertilizers
        )
        for f in top_fertilizers:
            f["confidence"] = 0.0

    # Build nutrient analysis
    nutrient_status = {
        "N": {"value": soil_N, "status": "Low" if soil_N < 50 else ("High" if soil_N > 100 else "Medium"),
              "color": "danger" if soil_N < 50 else ("warning" if soil_N > 100 else "success")},
        "P": {"value": soil_P, "status": "Low" if soil_P < 30 else ("High" if soil_P > 60 else "Medium"),
              "color": "danger" if soil_P < 30 else ("warning" if soil_P > 60 else "success")},
        "K": {"value": soil_K, "status": "Low" if soil_K < 30 else ("High" if soil_K > 80 else "Medium"),
              "color": "danger" if soil_K < 30 else ("warning" if soil_K > 80 else "success")},
        "ph": {"value": ph, "status": "Acidic" if ph < 6.0 else ("Alkaline" if ph > 7.5 else "Optimal"),
               "color": "warning" if ph < 6.0 or ph > 7.5 else "success"},
    }

    _save_history({
        "timestamp":  datetime.now().isoformat(),
        "crop":       crop,
        "soil":       {"N": soil_N, "P": soil_P, "K": soil_K, "ph": ph},
        "recommended": top_fertilizers[0]["name"] if top_fertilizers else "N/A"
    })

    return {
        "success":         True,
        "crop":            crop,
        "recommendations": top_fertilizers,
        "nutrient_status": nutrient_status,
        "model_used":      "RandomForest" if model_available else "Rule-Based",
    }
