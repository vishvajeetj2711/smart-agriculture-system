"""
Crop Recommendation Module
Uses a trained Random Forest model to recommend crops based on
soil parameters, weather conditions and season.
"""

import os
import json
import joblib
import numpy as np
from datetime import datetime

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(BASE_DIR, "models", "crop_model.pkl")
LE_PATH     = os.path.join(BASE_DIR, "models", "crop_label_encoder.pkl")
CROPS_JSON  = os.path.join(BASE_DIR, "data", "crops.json")
HISTORY_JSON= os.path.join(BASE_DIR, "data", "user_history.json")

SEASON_MAP  = {"Kharif": 0, "Rabi": 1, "Zaid": 2, "Annual": 3}
SOIL_MAP    = {"Clayey": 0, "Loamy": 1, "Sandy Loam": 2, "Black": 3,
               "Red": 2, "Alluvial": 1}

# Water availability score multipliers
WATER_AVAIL_MAP = {"High": 1.0, "Medium": 0.7, "Low": 0.4, "Rainfed": 0.5}


def _load_model():
    if not os.path.exists(MODEL_PATH):
        return None, None
    return joblib.load(MODEL_PATH), joblib.load(LE_PATH)


def _load_crops():
    with open(CROPS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)["crops"]


def _save_history(entry: dict):
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["crop_recommendations"].append(entry)
    # Keep last 50 entries
    history["crop_recommendations"] = history["crop_recommendations"][-50:]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def get_top_recommendations(N: float, P: float, K: float,
                             ph: float, rainfall: float,
                             season: str, soil_type: str,
                             organic_carbon: float = 0.5,
                             sand_pct: float = 33.0,
                             silt_pct: float = 33.0,
                             clay_pct: float = 34.0,
                             irrigation_available: str = "Yes",
                             water_source: str = "Borewell",
                             water_availability: str = "Medium",
                             irrigation_type: str = "Flood",
                             water_salinity: str = "Normal",
                             top_n: int = 3) -> dict:
    """
    Returns top N crop recommendations with confidence scores.
    New parameters: organic_carbon, soil texture (sand/silt/clay %),
    and full water/irrigation profile.
    Temperature and humidity removed — inferred from season + Gujarat context.
    """
    model, le = _load_model()
    crops_data = _load_crops()

    # Infer season-based temperature/humidity for Gujarat
    season_temp = {"Kharif": 30, "Rabi": 18, "Zaid": 35, "Annual": 27}
    season_hum  = {"Kharif": 70, "Rabi": 55, "Zaid": 40, "Annual": 60}
    temperature = season_temp.get(season, 28)
    humidity    = season_hum.get(season, 60)

    season_enc = SEASON_MAP.get(season, 0)
    soil_enc   = SOIL_MAP.get(soil_type, 1)

    features = np.array([[N, P, K, temperature, humidity, ph, rainfall,
                          season_enc, soil_enc]])

    if model is None:
        recommendations = _rule_based_recommend(
            N, P, K, temperature, humidity, ph, rainfall,
            season, soil_type, crops_data, top_n,
            organic_carbon=organic_carbon,
            sand_pct=sand_pct, silt_pct=silt_pct, clay_pct=clay_pct,
            water_availability=water_availability,
            water_source=water_source,
            irrigation_type=irrigation_type,
            irrigation_available=irrigation_available,
            water_salinity=water_salinity,
        )
    else:
        proba       = model.predict_proba(features)[0]
        top_indices = np.argsort(proba)[::-1][:top_n]
        crop_names  = le.inverse_transform(top_indices)
        confidences = proba[top_indices]

        recommendations = []
        for name, conf in zip(crop_names, confidences):
            crop_info = next((c for c in crops_data if c["name"] == name), {})
            recommendations.append({
                "crop":        name,
                "confidence":  round(float(conf) * 100, 1),
                "season":      crop_info.get("season", [season]),
                "water":       crop_info.get("water_requirement", "Medium"),
                "description": crop_info.get("description_en",
                               crop_info.get("description", "")),
                "icon":        crop_info.get("icon", "🌱"),
            })

    _save_history({
        "timestamp": datetime.now().isoformat(),
        "inputs": {
            "N": N, "P": P, "K": K, "ph": ph, "rainfall": rainfall,
            "season": season, "soil": soil_type,
            "organic_carbon": organic_carbon,
            "sand": sand_pct, "silt": silt_pct, "clay": clay_pct,
            "irrigation": irrigation_available, "water_source": water_source,
            "water_avail": water_availability, "irr_type": irrigation_type,
            "salinity": water_salinity,
        },
        "top_recommendation": recommendations[0]["crop"] if recommendations else "N/A"
    })

    return {
        "success":         True,
        "recommendations": recommendations,
        "input_summary":   {
            "soil_type":    soil_type,
            "season":       season,
            "ph":           ph,
            "N":            N,
            "P":            P,
            "K":            K,
            "organic_carbon": organic_carbon,
            "texture":      f"Sand {sand_pct}% / Silt {silt_pct}% / Clay {clay_pct}%",
            "irrigation":   irrigation_available,
            "water_source": water_source,
            "water_avail":  water_availability,
            "irr_type":     irrigation_type,
            "salinity":     water_salinity,
        }
    }


def _rule_based_recommend(N, P, K, temp, humidity, ph, rainfall,
                          season, soil_type, crops_data, top_n,
                          organic_carbon=0.5, sand_pct=33, silt_pct=33,
                          clay_pct=34, water_availability="Medium",
                          water_source="Borewell", irrigation_type="Flood",
                          irrigation_available="Yes", water_salinity="Normal"):
    """
    Enhanced rule-based scoring that factors in organic carbon,
    soil texture, and water/irrigation profile.
    """
    water_score_mult = WATER_AVAIL_MAP.get(water_availability, 0.7)
    if irrigation_available == "No":
        water_score_mult = min(water_score_mult, 0.4)

    scores = []
    for crop in crops_data:
        score = 0

        # Season match (high weight)
        if season in crop.get("season", []):
            score += 30

        # Soil type match
        if soil_type in crop.get("soil_types", []):
            score += 18

        # pH suitability
        p_range = crop.get("ph_range", [5, 8])
        if p_range[0] <= ph <= p_range[1]:
            score += 14
        elif abs(ph - (p_range[0] + p_range[1]) / 2) < 1:
            score += 6

        # Rainfall vs crop water requirement
        r_range = crop.get("rainfall_mm", [0, 500])
        if r_range[0] <= rainfall <= r_range[1]:
            score += 14
        elif rainfall < r_range[0]:
            # Can supplement with irrigation?
            if water_availability in ("High", "Medium") and irrigation_available == "Yes":
                score += 8
        else:
            score += 6

        # Water requirement vs availability
        crop_water = crop.get("water_requirement", "Medium")
        if crop_water == "High":
            score += int(14 * water_score_mult)
        elif crop_water == "Medium":
            score += int(10 * water_score_mult)
        else:
            score += 10  # Low water crops always suitable

        # Organic carbon bonus
        if organic_carbon >= 1.0:
            score += 6
        elif organic_carbon >= 0.5:
            score += 3

        # Soil texture suitability
        # Sandy soils (sand>60%): favour groundnut, castor, cumin, bajra
        # Clayey soils (clay>40%): favour rice, sugarcane, cotton
        # Loamy (balanced): favour most crops
        if sand_pct > 60 and crop.get("name") in ["Groundnut","Castor","Cumin","Bajra"]:
            score += 8
        elif clay_pct > 40 and crop.get("name") in ["Rice","Sugarcane","Cotton"]:
            score += 8
        elif 20 <= sand_pct <= 60 and 15 <= clay_pct <= 40:
            score += 5  # loamy texture suits most crops

        # Irrigation type bonus for high-water crops
        if irrigation_type in ("Drip", "Sprinkler") and crop_water in ("High", "Medium"):
            score += 4
        if water_salinity == "High" and crop.get("name") in ["Cotton", "Bajra", "Castor"]:
            score += 6  # salt-tolerant crops bonus

        scores.append((crop["name"], score, crop))

    scores.sort(key=lambda x: x[1], reverse=True)
    result = []
    for name, score, crop in scores[:top_n]:
        result.append({
            "crop":        name,
            "confidence":  round(min(score, 100), 1),
            "season":      crop.get("season", []),
            "water":       crop.get("water_requirement", "Medium"),
            "description": crop.get("description_en", crop.get("description", "")),
            "icon":        crop.get("icon", "🌱"),
        })
    return result

    scores.sort(key=lambda x: x[1], reverse=True)
    result = []
    for name, score, crop in scores[:top_n]:
        result.append({
            "crop":        name,
            "hindi":       crop.get("hindi", ""),
            "confidence":  round(min(score, 100), 1),
            "season":      crop.get("season", []),
            "water":       crop.get("water_requirement", "Medium"),
            "description": crop.get("description", ""),
            "icon":        crop.get("icon", "🌱"),
        })
    return result
