"""
Smart Irrigation & Water Management Decision Engine
====================================================
Deterministic rule-based agronomic irrigation calculation service for Gujarat agriculture.
No external database used — data stored in JSON files and localStorage.
"""

import os
import json
from datetime import datetime

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IRRIGATION_JSON = os.path.join(BASE_DIR, "data", "irrigation.json")
CROP_WATER_JSON = os.path.join(BASE_DIR, "data", "crop-water-requirements.json")
HISTORY_JSON    = os.path.join(BASE_DIR, "data", "user_history.json")


def load_irrigation_rules() -> dict:
    """Load configurable crop irrigation rules and global factors from JSON."""
    if not os.path.exists(IRRIGATION_JSON):
        return {"crops": {}, "growthStageFactors": {}, "irrigationEfficiency": {}, "soilFactors": {}}
    with open(IRRIGATION_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_crop_water_requirements() -> dict:
    """Load crop agronomic water requirements reference data from JSON."""
    if not os.path.exists(CROP_WATER_JSON):
        return {"crops": {}}
    with open(CROP_WATER_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def get_crop_irrigation_rule(crop_name: str) -> dict:
    """Get crop irrigation configuration by name with fallback defaults."""
    rules = load_irrigation_rules()
    crops = rules.get("crops", {})

    if crop_name in crops:
        return crops[crop_name]

    # Case-insensitive / partial match search
    for name, data in crops.items():
        if name.lower() == str(crop_name).lower():
            return data

    # Default fallback
    return {
        "crop": crop_name or "General Crop",
        "gujarati": "સામાન્ય પાક",
        "icon": "🌱",
        "minimumMoisture": 30,
        "idealMoistureMin": 45,
        "idealMoistureMax": 65,
        "criticalMoisture": 20,
        "baseWaterPerAcre": 20000,
        "preferredIrrigationTime": ["Morning", "Evening"],
        "criticalStages": ["Vegetative", "Flowering"],
        "rootDepth": "Medium (60 cm)",
        "soilPreference": ["Loamy"],
        "description": "General agricultural crop configured with standard baseline parameters.",
        "description_gu": "સામાન્ય પાક માટે સ્ટાન્ડર્ડ સરેરાશ પિયત પરિમાણો."
    }


def evaluate_rainfall_risk(rain_prob: float, expected_rainfall: float) -> bool:
    """
    Rule A Evaluation:
    If rain probability >= 70% AND expected rainfall is significant (>= 5mm or > 0 with >=75% prob).
    """
    if rain_prob >= 70.0 and expected_rainfall >= 5.0:
        return True
    if rain_prob >= 80.0 and expected_rainfall >= 2.0:
        return True
    if rain_prob >= 85.0:
        return True
    return False


def calculate_water_requirement(crop_rule: dict,
                                land_area: float,
                                growth_stage: str,
                                soil_type: str,
                                irrigation_method: str,
                                soil_moisture: float,
                                expected_rainfall: float = 0.0,
                                water_availability: str = "Medium") -> dict:
    """
    Calculate estimated applied water in Liters based on:
    - Land area
    - Base crop requirement
    - Crop growth stage factor
    - Soil type holding factor
    - Water availability factor
    - Soil moisture deficit
    - Irrigation method efficiency
    - Expected rainfall offset
    """
    rules = load_irrigation_rules()
    stage_factors = rules.get("growthStageFactors", {
        "Seedling": 0.8, "Vegetative": 1.0, "Flowering": 1.2, "Fruiting": 1.2, "Maturity": 0.8
    })
    efficiency_map = rules.get("irrigationEfficiency", {
        "Drip": 0.90, "Sprinkler": 0.75, "Flood": 0.60, "Furrow": 0.65
    })
    soil_map = rules.get("soilFactors", {
        "Sandy Loam": 1.15, "Loamy": 1.00, "Black": 0.90, "Clayey": 0.85, "Red": 1.05, "Alluvial": 0.95
    })
    water_avail_map = rules.get("waterAvailabilityFactors", {
        "High": 1.00, "Medium": 0.90, "Low": 0.75
    })

    stage_factor  = stage_factors.get(growth_stage, 1.0)
    efficiency    = efficiency_map.get(irrigation_method, 0.60)
    soil_factor   = soil_map.get(soil_type, 1.0)
    avail_factor  = water_avail_map.get(water_availability, 0.9)

    base_per_acre = crop_rule.get("baseWaterPerAcre", 20000)
    base_water    = land_area * base_per_acre * stage_factor

    # Moisture deficit multiplier:
    # If soil is below ideal minimum, scale requirement proportionally
    ideal_min = crop_rule.get("idealMoistureMin", 50)
    ideal_max = crop_rule.get("idealMoistureMax", 65)
    crit_min  = crop_rule.get("criticalMoisture", 25)

    if soil_moisture < ideal_min:
        # Range deficit: 0.5 at ideal_min down to 1.3 at critical or below
        denom = max(1.0, float(ideal_max - crit_min))
        moisture_multiplier = max(0.4, min(1.4, (ideal_max - soil_moisture) / denom))
    else:
        moisture_multiplier = 0.0

    # Net crop water needed
    net_water = base_water * moisture_multiplier * soil_factor * avail_factor

    # Applied water adjusted for system efficiency
    if efficiency > 0 and net_water > 0:
        applied_water = net_water / efficiency
    else:
        applied_water = 0.0

    # Rainfall offset: 1 mm over 1 acre = 4046.86 Liters
    if expected_rainfall > 0 and applied_water > 0:
        rain_volume_L = expected_rainfall * 4046.86 * land_area
        applied_water = max(0.0, applied_water - rain_volume_L)

    # Comparison metrics (Efficiency comparison)
    flood_water = (net_water / 0.60) if net_water > 0 else 0
    drip_water  = (net_water / 0.90) if net_water > 0 else 0
    water_saved_with_drip = max(0, round(flood_water - drip_water))

    return {
        "applied_water_L":        round(applied_water),
        "net_water_L":            round(net_water),
        "flood_equivalent_L":     round(flood_water),
        "drip_equivalent_L":      round(drip_water),
        "water_saved_with_drip_L": water_saved_with_drip,
        "efficiency_pct":         round(efficiency * 100),
        "stage_factor":           stage_factor,
        "soil_factor":            soil_factor,
        "avail_factor":           avail_factor,
        "moisture_multiplier":    round(moisture_multiplier, 2)
    }


def generate_farmer_advice(status: str,
                           crop: str,
                           soil_moisture: float,
                           rain_prob: float,
                           expected_rainfall: float,
                           temp: float,
                           growth_stage: str,
                           method: str,
                           est_water: int) -> dict:
    """
    Generate bilingual (English & Gujarati) farmer-friendly actionable advice.
    Does not make independent decisions; translates deterministic calculation.
    """
    if status == "WAIT":
        return {
            "en": f"Heavy rainfall ({expected_rainfall} mm, {rain_prob}% probability) is expected soon. Postpone irrigation to prevent waterlogging, nutrient leaching, and unnecessary electricity/water cost. Check field drainage and monitor soil moisture after the rain stops.",
            "gu": f"ખેતરમાં નોંધપાત્ર વરસાદ ({expected_rainfall} મીમી, {rain_prob}% સંભાવના) ની આગાહી છે. હાલ પિયત મુલતવી રાખો જેથી પાણી ભરાઈ ન જાય, ખાતર વહી ન જાય અને વીજળી/પાણીનો બગાડ અટકે. વરસાદ પછી જમીનનો ભેજ ચકાસી આગળનો નિર્ણય લો."
        }
    elif status == "HIGH":
        return {
            "en": f"Your {crop} field is experiencing critical water stress (soil moisture is only {soil_moisture}%). Apply approximately {est_water:,} L using your {method} irrigation system during early morning or evening hours. Monitor soil moisture 24 hours post-irrigation.",
            "gu": f"તમારા {crop} ના પાકમાં પાણીની ગંભીર તાણ છે (જમીનનો ભેજ માત્ર {soil_moisture}% છે). વહેલી સવારે અથવા સાંજે {method} પદ્ધતિથી અંદાજે {est_water:,} લીટર પિયત આપવાની ભલામણ છે. પિયત આપ્યાના ૨૪ કલાક પછી ફરી ભેજ ચકાસો."
        }
    elif status == "MEDIUM":
        return {
            "en": f"Soil moisture ({soil_moisture}%) is below optimal range for {crop} at {growth_stage} stage. Moderate water stress detected. Plan an irrigation session of about {est_water:,} L within the next 24-48 hours.",
            "gu": f"{crop} ના પાકમાં {growth_stage} અવસ્થાએ જમીનનો ભેજ ({soil_moisture}%) ઘટવા લાગ્યો છે. મધ્યમ તાણ જોવા મળે છે. આગામી ૨૪ થી ૪૮ કલાકમાં અંદાજે {est_water:,} લીટર પિયતનું આયોજન કરો."
        }
    elif status == "LOW":
        return {
            "en": f"Soil moisture ({soil_moisture}%) is optimal and well within the target range for {crop}. No irrigation is required at this time. Maintain routine field inspection.",
            "gu": f"જમીનનો ભેજ ({soil_moisture}%) {crop} ના પાક માટે આદર્શ અને પૂરતા પ્રમાણમાં છે. હાલ પિયત આપવાની જરૂર નથી. સામાન્ય નિરીક્ષણ ચાલુ રાખો."
        }
    elif status == "NO_IRRIGATION":
        return {
            "en": f"Soil moisture is excessively high ({soil_moisture}%). Additional irrigation is NOT recommended as it may cause root suffocation and fungal infection. Ensure field drainage channels are open.",
            "gu": f"જમીનમાં ભેજનું પ્રમાણ ખૂબ વધારે ({soil_moisture}%) છે. વધુ પિયત આપવાથી મૂળનો સડો અને ફૂગજન્ય રોગોનું જોખમ રહે છે. ખેતરમાંથી વધારાના પાણીના નિકાલની વ્યવસ્થા રાખો."
        }
    else:
        return {
            "en": f"Monitor your {crop} field condition and check soil moisture regularly.",
            "gu": f"તમારા {crop} પાકની પરિસ્થિતિ અને જમીનનો ભેજ નિયમિત ચકાસતા રહો."
        }


def calculate_irrigation_recommendation(crop: str = "Cotton",
                                        growth_stage: str = "Vegetative",
                                        land_area: float = 1.0,
                                        soil_type: str = "Loamy",
                                        soil_moisture: float = 50.0,
                                        soil_ph: float = 7.0,
                                        irrigation_method: str = "Flood",
                                        water_availability: str = "Medium",
                                        last_irrigation_date: str = "",
                                        weather_temp: float = 32.0,
                                        weather_humidity: float = 55.0,
                                        rain_prob: float = 10.0,
                                        expected_rainfall: float = 0.0,
                                        wind_speed: float = 3.5) -> dict:
    """
    Deterministic Irrigation Decision Engine
    Evaluates:
    1. Soil moisture
    2. Crop-specific moisture thresholds from JSON
    3. Rain probability & expected rainfall (Rule A)
    4. Temperature & humidity
    5. Crop growth stage
    6. Irrigation method & efficiency
    7. Water availability
    8. Last irrigation date
    """
    # Validation & normalization
    crop_name = crop.strip() if crop else "Cotton"
    try:
        land_area = max(0.1, float(land_area))
    except (ValueError, TypeError):
        land_area = 1.0

    try:
        soil_moisture = max(0.0, min(100.0, float(soil_moisture)))
    except (ValueError, TypeError):
        soil_moisture = 50.0

    try:
        soil_ph = max(3.0, min(10.0, float(soil_ph)))
    except (ValueError, TypeError):
        soil_ph = 7.0

    try:
        weather_temp = float(weather_temp)
    except (ValueError, TypeError):
        weather_temp = 32.0

    try:
        weather_humidity = float(weather_humidity)
    except (ValueError, TypeError):
        weather_humidity = 55.0

    try:
        rain_prob = max(0.0, min(100.0, float(rain_prob)))
    except (ValueError, TypeError):
        rain_prob = 0.0

    try:
        expected_rainfall = max(0.0, float(expected_rainfall))
    except (ValueError, TypeError):
        expected_rainfall = 0.0

    try:
        wind_speed = float(wind_speed)
    except (ValueError, TypeError):
        wind_speed = 3.5

    crop_rule = get_crop_irrigation_rule(crop_name)

    critical_moist = crop_rule.get("criticalMoisture", 25)
    minimum_moist  = crop_rule.get("minimumMoisture", 35)
    ideal_min      = crop_rule.get("idealMoistureMin", 50)
    ideal_max      = crop_rule.get("idealMoistureMax", 65)

    # ── DECISION RULES (Deterministic Evaluation) ────────────────────────
    rule_applied = ""
    status = "LOW"
    irrigation_required = False
    water_stress = "Low"
    reason = ""

    # Rule A: Heavy expected rainfall
    if evaluate_rainfall_risk(rain_prob, expected_rainfall):
        status = "WAIT"
        irrigation_required = False
        water_stress = "Low / Rain Delay"
        rule_applied = "Rule A — Heavy Expected Rainfall"
        reason = (
            f"Significant rainfall is expected (Rain probability: {rain_prob}%, "
            f"Expected rain: {expected_rainfall} mm). Irrigation can be delayed and soil moisture should be monitored."
        )

    # Rule E: Excessive moisture (High saturation)
    elif soil_moisture > ideal_max or soil_moisture >= 80.0:
        status = "NO_IRRIGATION"
        irrigation_required = False
        water_stress = "None / Saturated"
        rule_applied = "Rule E — Excessive Soil Moisture"
        reason = (
            f"Soil moisture ({soil_moisture}%) is already high and exceeds the configured ideal threshold "
            f"({ideal_max}%). Additional irrigation is not recommended at this time to avoid root rot."
        )

    # Rule B: Critical soil moisture
    elif soil_moisture <= critical_moist:
        status = "HIGH"
        irrigation_required = True
        water_stress = "High"
        rule_applied = "Rule B — Critical Soil Moisture"
        reason = (
            f"Soil moisture ({soil_moisture}%) is at or below the crop critical moisture threshold "
            f"({critical_moist}%) and significant rainfall is not expected. Immediate irrigation is recommended."
        )

    # Rule C: Moisture below minimum
    elif soil_moisture < minimum_moist:
        status = "MEDIUM"
        irrigation_required = True
        water_stress = "Moderate"
        rule_applied = "Rule C — Moisture Below Minimum"
        reason = (
            f"Soil moisture ({soil_moisture}%) is below the configured minimum threshold "
            f"({minimum_moist}%) and rain probability is low/moderate ({rain_prob}%)."
        )

    # Rule D: Moisture within ideal range
    elif ideal_min <= soil_moisture <= ideal_max:
        status = "LOW"
        irrigation_required = False
        water_stress = "Low"
        rule_applied = "Rule D — Moisture Within Ideal Range"
        reason = (
            f"Soil moisture ({soil_moisture}%) is currently within the configured target range "
            f"({ideal_min}% - {ideal_max}%)."
        )

    # Intermediate Zone: between minimumMoisture and idealMoistureMin
    else:  # minimum_moist <= soil_moisture < ideal_min
        if weather_temp > 35.0 or water_availability == "Low":
            status = "MEDIUM"
            irrigation_required = True
            water_stress = "Moderate"
            rule_applied = "Rule C (Adjusted) — Approaching Minimum Under High Heat"
            reason = (
                f"Soil moisture ({soil_moisture}%) is approaching the minimum threshold ({minimum_moist}%) "
                f"under high evaporative temperature ({weather_temp}°C). Light irrigation is recommended."
            )
        else:
            status = "LOW"
            irrigation_required = False
            water_stress = "Low / Monitor"
            rule_applied = "Rule D (Adjusted) — Adequate Moisture (Monitor)"
            reason = (
                f"Soil moisture ({soil_moisture}%) is acceptable but approaching minimum threshold ({minimum_moist}%). "
                f"Continue monitoring field moisture."
            )

    # Water requirement calculation
    water_calc = calculate_water_requirement(
        crop_rule=crop_rule,
        land_area=land_area,
        growth_stage=growth_stage,
        soil_type=soil_type,
        irrigation_method=irrigation_method,
        soil_moisture=soil_moisture,
        expected_rainfall=expected_rainfall if status != "WAIT" else 0.0,
        water_availability=water_availability
    )

    if not irrigation_required:
        estimated_water_L = 0
    else:
        estimated_water_L = water_calc["applied_water_L"]

    # Recommended Best Irrigation Time
    if status == "WAIT":
        recommended_time = "Wait until after rainfall"
        time_reason = "Rainfall forecasted; delay irrigation until post-rain soil assessment"
    elif status == "NO_IRRIGATION":
        recommended_time = "No irrigation required"
        time_reason = "Soil moisture is already at or above saturation capacity"
    elif not irrigation_required:
        recommended_time = "No irrigation required today"
        time_reason = "Soil moisture is in optimal balance"
    else:
        if weather_temp >= 33.0:
            recommended_time = "Early Morning (06:00 AM - 08:00 AM) or Late Evening (06:00 PM - 07:30 PM)"
            time_reason = "High daytime temperature (>33°C) increases evaporation loss during midday"
        else:
            preferred = crop_rule.get("preferredIrrigationTime", ["Morning", "Evening"])
            recommended_time = " / ".join(preferred)
            time_reason = "Optimal ambient conditions for soil absorption and root uptake"

    # Status color and badges
    status_config = {
        "HIGH": {
            "badge_class": "danger",
            "bg_soft": "bg-danger-soft",
            "text_color": "danger",
            "icon": "🔴",
            "title": "HIGH WATER STRESS",
            "subtitle": "IRRIGATION REQUIRED IMMEDIATELY",
            "color_hex": "#c62828"
        },
        "MEDIUM": {
            "badge_class": "warning",
            "bg_soft": "bg-warning-soft",
            "text_color": "warning",
            "icon": "🟡",
            "title": "MODERATE WATER STRESS",
            "subtitle": "IRRIGATION RECOMMENDED SOON",
            "color_hex": "#e65100"
        },
        "LOW": {
            "badge_class": "success",
            "bg_soft": "bg-success-soft",
            "text_color": "success",
            "icon": "🟢",
            "title": "LOW WATER STRESS",
            "subtitle": "NO IRRIGATION REQUIRED",
            "color_hex": "#2e7d32"
        },
        "WAIT": {
            "badge_class": "info",
            "bg_soft": "bg-info-soft",
            "text_color": "info",
            "icon": "🔵",
            "title": "WAIT — RAIN EXPECTED",
            "subtitle": "DELAY IRRIGATION AND MONITOR FIELD",
            "color_hex": "#0288d1"
        },
        "NO_IRRIGATION": {
            "badge_class": "secondary",
            "bg_soft": "bg-secondary-soft",
            "text_color": "secondary",
            "icon": "⚪",
            "title": "SOIL SATURATED",
            "subtitle": "NO ADDITIONAL IRRIGATION NEEDED",
            "color_hex": "#546e7a"
        }
    }
    status_ui = status_config.get(status, status_config["LOW"])

    # Generate bilingual farmer advice
    farmer_advice = generate_farmer_advice(
        status=status,
        crop=crop_name,
        soil_moisture=soil_moisture,
        rain_prob=rain_prob,
        expected_rainfall=expected_rainfall,
        temp=weather_temp,
        growth_stage=growth_stage,
        method=irrigation_method,
        est_water=estimated_water_L
    )

    # WhatsApp Alert ready text
    alert_text = (
        f"🌾 *SMART AGRICULTURE SYSTEM — GUJARAT*\n"
        f"💧 *Smart Irrigation & Water Advisory*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌱 *Crop:* {crop_name} ({land_area} Acres) · {growth_stage}\n"
        f"📊 *Status:* {status_ui['icon']} *{status_ui['title']}*\n"
        f"💧 *Soil Moisture:* {soil_moisture}%\n"
        f"🌧️ *Rain Forecast:* {rain_prob}% (Expected: {expected_rainfall} mm)\n"
        f"🚰 *Estimated Water:* {estimated_water_L:,} Liters ({irrigation_method})\n"
        f"⏰ *Recommended Time:* {recommended_time}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Advisory (English):*\n{farmer_advice['en']}\n\n"
        f"🌾 *ખેડૂત સલાહ (Gujarati):*\n{farmer_advice['gu']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🙏 _Sent by Smart Agriculture Irrigation Agent_"
    )

    # Technical viva / exam breakdown
    technical_details = {
        "formula": (
            "Estimated Applied Water (L) = [Land Area (Acres) × Base Crop Water (L/Acre) × Growth Stage Factor × "
            "Moisture Deficit Ratio × Soil Factor × Water Avail Factor - Rain Offset (L)] ÷ Irrigation Method Efficiency"
        ),
        "inputs": {
            "land_area": land_area,
            "crop": crop_name,
            "soil_type": soil_type,
            "soil_moisture": soil_moisture,
            "soil_ph": soil_ph,
            "growth_stage": growth_stage,
            "irrigation_method": irrigation_method,
            "water_availability": water_availability,
            "last_irrigation_date": last_irrigation_date or "Not specified",
            "weather_temp": weather_temp,
            "weather_humidity": weather_humidity,
            "rain_prob": rain_prob,
            "expected_rainfall_mm": expected_rainfall,
            "wind_speed_ms": wind_speed
        },
        "factors_applied": {
            "baseWaterPerAcre": crop_rule.get("baseWaterPerAcre", 20000),
            "criticalMoisture": critical_moist,
            "minimumMoisture": minimum_moist,
            "idealMoistureMin": ideal_min,
            "idealMoistureMax": ideal_max,
            "growthStageMultiplier": water_calc["stage_factor"],
            "soilFactor": water_calc["soil_factor"],
            "waterAvailabilityMultiplier": water_calc["avail_factor"],
            "moistureDeficitMultiplier": water_calc["moisture_multiplier"],
            "irrigationEfficiency": f"{water_calc['efficiency_pct']}%",
            "rule_applied": rule_applied
        }
    }

    result = {
        "success": True,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "date_str": datetime.now().strftime("%d %b %Y"),
        "crop": crop_name,
        "crop_gujarati": crop_rule.get("gujarati", crop_name),
        "crop_icon": crop_rule.get("icon", "🌱"),
        "growth_stage": growth_stage,
        "land_area": land_area,
        "soil_type": soil_type,
        "soil_moisture": soil_moisture,
        "soil_ph": soil_ph,
        "irrigation_method": irrigation_method,
        "water_availability": water_availability,
        "last_irrigation_date": last_irrigation_date,
        "status": status,
        "status_ui": status_ui,
        "irrigation_required": irrigation_required,
        "water_stress": water_stress,
        "estimated_water_L": estimated_water_L,
        "estimated_water_formatted": f"{estimated_water_L:,} L" if estimated_water_L > 0 else "0 L (No Irrigation)",
        "recommended_time": recommended_time,
        "time_reason": time_reason,
        "reason": reason,
        "rule_applied": rule_applied,
        "farmer_advice": farmer_advice,
        "water_calc": water_calc,
        "alert_text": alert_text,
        "weather_summary": {
            "temp": weather_temp,
            "humidity": weather_humidity,
            "rain_prob": rain_prob,
            "expected_rainfall": expected_rainfall,
            "wind_speed": wind_speed
        },
        "technical_details": technical_details,
        "disclaimer": "Configured project estimation for Gujarat agro-climatic conditions. Actual water requirements depend on real-time field variations."
    }

    return result


def save_irrigation_history(entry: dict) -> list:
    """Save an irrigation calculation result to JSON user history (no database)."""
    try:
        history = {"crop_recommendations": [], "irrigation_logs": [], "disease_detections": [], "weather_queries": [], "market_queries": []}
        if os.path.exists(HISTORY_JSON):
            with open(HISTORY_JSON, "r", encoding="utf-8") as f:
                history = json.load(f)

        if "irrigation_logs" not in history:
            history["irrigation_logs"] = []

        log_item = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%d %b %Y %H:%M"),
            "crop": entry.get("crop", "Cotton"),
            "growth_stage": entry.get("growth_stage", "Vegetative"),
            "area_acres": entry.get("land_area", 1.0),
            "soil_type": entry.get("soil_type", "Loamy"),
            "soil_moisture": entry.get("soil_moisture", 50),
            "method": entry.get("irrigation_method", "Flood"),
            "water_estimated_L": entry.get("estimated_water_L", 0),
            "status": entry.get("status", "LOW"),
            "water_stress": entry.get("water_stress", "Low"),
            "recommended_time": entry.get("recommended_time", "Morning"),
            "rain_prob": entry.get("weather_summary", {}).get("rain_prob", 0)
        }

        history["irrigation_logs"].append(log_item)
        history["irrigation_logs"] = history["irrigation_logs"][-50:]  # keep last 50

        with open(HISTORY_JSON, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

        return history["irrigation_logs"]
    except Exception as e:
        print(f"Error saving irrigation history: {e}")
        return []


def get_irrigation_history(limit: int = 10) -> list:
    """Retrieve the recent irrigation calculation logs from JSON history."""
    try:
        if not os.path.exists(HISTORY_JSON):
            return []
        with open(HISTORY_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_logs = data.get("irrigation_logs", [])
        normalized = []
        for log in raw_logs:
            normalized.append({
                "timestamp":          log.get("timestamp", ""),
                "date":               log.get("date", log.get("timestamp", "")[:16] if log.get("timestamp") else ""),
                "crop":               log.get("crop", "Cotton"),
                "growth_stage":       log.get("growth_stage", "Vegetative"),
                "area_acres":         log.get("area_acres", log.get("area", 1.0)),
                "soil_type":          log.get("soil_type", "Loamy"),
                "soil_moisture":      log.get("soil_moisture", 50),
                "method":             log.get("method", "Flood"),
                "water_estimated_L":  log.get("water_estimated_L", 0),
                "status":             log.get("status", "LOW"),
                "water_stress":       log.get("water_stress", "Low"),
                "recommended_time":   log.get("recommended_time", "Morning"),
                "rain_prob":          log.get("rain_prob", 0),
            })
        return normalized[-limit:][::-1]  # Most recent first
    except Exception as e:
        print(f"Error reading irrigation history: {e}")
        return []
