"""
Irrigation Scheduler Module
Generates smart irrigation schedules based on crop water needs,
weather data, and soil moisture.
"""

import os
import json
from datetime import datetime, timedelta

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE_JSON = os.path.join(BASE_DIR, "data", "irrigation_schedule.json")
HISTORY_JSON  = os.path.join(BASE_DIR, "data", "user_history.json")


def _load_schedule_data():
    with open(SCHEDULE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_schedule_data(data: dict):
    with open(SCHEDULE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _save_history(entry: dict):
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["irrigation_logs"].append(entry)
    history["irrigation_logs"] = history["irrigation_logs"][-50:]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _get_irrigation_method_details(method: str) -> dict:
    methods = {
        "Drip":    {"efficiency": 0.90, "flow_lph": 4,   "cost_per_acre": 35000},
        "Sprinkler":{"efficiency": 0.75, "flow_lph": 200, "cost_per_acre": 20000},
        "Flood":   {"efficiency": 0.50, "flow_lph": 1000,"cost_per_acre": 5000},
        "Furrow":  {"efficiency": 0.55, "flow_lph": 600, "cost_per_acre": 8000},
    }
    return methods.get(method, methods["Flood"])


def generate_schedule(crop: str, area_acres: float, soil_moisture: float,
                      irrigation_method: str, weather_temp: float = 28,
                      weather_humidity: float = 60,
                      rainfall_last_7days_mm: float = 0) -> dict:
    """
    Generate a 7-day irrigation schedule based on crop, area, soil moisture,
    and current weather conditions.
    """
    sched_data = _load_schedule_data()
    crop_water  = sched_data.get("crops_water_need", {})
    crop_info   = crop_water.get(crop, crop_water.get("Other", {"daily_mm": 4, "frequency_days": 3}))

    daily_mm       = crop_info["daily_mm"]
    freq_days      = crop_info["frequency_days"]
    method_details = _get_irrigation_method_details(irrigation_method)
    efficiency     = method_details["efficiency"]

    # Adjust for weather
    if weather_temp > 35:
        daily_mm *= 1.3   # Higher evapotranspiration in heat
    elif weather_temp < 20:
        daily_mm *= 0.8

    if weather_humidity > 80:
        daily_mm *= 0.85
    elif weather_humidity < 40:
        daily_mm *= 1.2

    # Reduce for recent rainfall
    if rainfall_last_7days_mm > 50:
        daily_mm *= 0.3
    elif rainfall_last_7days_mm > 25:
        daily_mm *= 0.6
    elif rainfall_last_7days_mm > 10:
        daily_mm *= 0.85

    # Soil moisture correction
    soil_deficit  = max(0, 60 - soil_moisture)  # target 60% moisture
    extra_water   = soil_deficit * 0.5          # mm to make up deficit

    # Water volume per irrigation session (liters per acre)
    MM_TO_LITERS_PER_ACRE = 4046.86  # 1 mm depth over 1 acre
    water_per_session_L   = ((daily_mm * freq_days) + extra_water) / efficiency * MM_TO_LITERS_PER_ACRE * area_acres

    # Time per session (minutes) based on method flow rate
    flow_lph     = method_details["flow_lph"]
    duration_min = max(15, round(water_per_session_L / flow_lph * 60))

    # Determine best irrigation time
    if weather_temp > 30:
        best_time = "06:00 AM"
        time_reason = "Early morning to minimize evaporation"
    elif weather_humidity > 80:
        best_time = "10:00 AM"
        time_reason = "Mid-morning when humidity drops"
    else:
        best_time = "07:00 AM"
        time_reason = "Morning irrigation for best absorption"

    # Generate 7-day schedule
    today    = datetime.now()
    schedule = []
    for day_offset in range(7):
        date = today + timedelta(days=day_offset)
        needs_irrigation = (day_offset % freq_days == 0)

        # Override if heavy rain expected (simplified)
        if needs_irrigation:
            status = "Irrigate"
            status_color = "success"
            water_L = round(water_per_session_L)
        else:
            status = "Rest Day"
            status_color = "secondary"
            water_L = 0

        # First day soil moisture override
        if day_offset == 0 and soil_moisture > 70:
            status = "Skip — Soil Moist"
            status_color = "info"
            water_L = 0

        schedule.append({
            "date":         date.strftime("%d %b"),
            "day":          date.strftime("%A"),
            "status":       status,
            "status_color": status_color,
            "time":         best_time if status == "Irrigate" else "—",
            "duration_min": duration_min if status == "Irrigate" else 0,
            "water_L":      water_L,
        })

    # Weekly summary
    total_sessions = sum(1 for s in schedule if s["status"] == "Irrigate")
    total_water_L  = sum(s["water_L"] for s in schedule)

    # Soil moisture alert
    if soil_moisture < 30:
        alert = {"type": "danger", "message": f"⚠️ Critical: Soil moisture is very low ({soil_moisture}%). Irrigate immediately!"}
    elif soil_moisture < 45:
        alert = {"type": "warning", "message": f"⚡ Soil moisture is low ({soil_moisture}%). Irrigate at next scheduled time."}
    elif soil_moisture > 80:
        alert = {"type": "info", "message": f"✅ Soil moisture is adequate ({soil_moisture}%). You can skip the next irrigation."}
    else:
        alert = {"type": "success", "message": f"✅ Soil moisture is optimal ({soil_moisture}%). Follow the schedule normally."}

    # Save current schedule
    new_entry = {
        "id":           datetime.now().strftime("%Y%m%d%H%M%S"),
        "created":      datetime.now().isoformat(),
        "crop":         crop,
        "area_acres":   area_acres,
        "method":       irrigation_method,
        "soil_moisture":soil_moisture,
        "schedule":     schedule,
    }
    sched_data.setdefault("schedules", [])
    sched_data["schedules"].append(new_entry)
    sched_data["schedules"] = sched_data["schedules"][-20:]
    _save_schedule_data(sched_data)

    _save_history({
        "timestamp":    datetime.now().isoformat(),
        "crop":         crop,
        "area":         area_acres,
        "method":       irrigation_method,
        "soil_moisture":soil_moisture,
        "sessions_week":total_sessions,
    })

    return {
        "success":         True,
        "crop":            crop,
        "area_acres":      area_acres,
        "method":          irrigation_method,
        "schedule":        schedule,
        "best_time":       best_time,
        "time_reason":     time_reason,
        "duration_min":    duration_min,
        "water_per_session_L": round(water_per_session_L),
        "total_water_week_L":  round(total_water_L),
        "total_sessions":      total_sessions,
        "daily_water_mm":      round(daily_mm, 1),
        "alert":               alert,
        "method_efficiency":   round(efficiency * 100),
    }


def get_history() -> list:
    """Return last 10 saved irrigation schedules."""
    data = _load_schedule_data()
    return data.get("schedules", [])[-10:]


# ── Bridge & Re-export Smart Irrigation Engine (Snake & Camel Case) ─
from modules.smart_irrigation import (
    load_irrigation_rules,
    load_crop_water_requirements,
    get_crop_irrigation_rule,
    evaluate_rainfall_risk,
    calculate_water_requirement,
    calculate_irrigation_recommendation,
    generate_farmer_advice,
    save_irrigation_history,
    get_irrigation_history,
)

# CamelCase aliases as requested in prompt requirements
getCropIrrigationRule               = get_crop_irrigation_rule
calculateWaterRequirement           = calculate_water_requirement
evaluateRainfallRisk                = evaluate_rainfall_risk
calculateIrrigationRecommendation   = calculate_irrigation_recommendation
generateFarmerAdvice                = generate_farmer_advice
saveIrrigationHistory               = save_irrigation_history
getIrrigationHistory                = get_irrigation_history

