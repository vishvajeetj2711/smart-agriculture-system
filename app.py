"""
Smart Agriculture System - Main Flask Application
Run: python app.py
Then open: http://localhost:5000
"""

import os
import json
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename

# ── Path setup ───────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Imports from modules ─────────────────────────────────────────
from modules.crop_recommendation    import get_top_recommendations
from modules.disease_detection      import detect_disease, allowed_file
from modules.weather_advisory       import get_weather, get_forecast, GUJARAT_CITIES
from modules.market_prices          import get_market_prices, get_gujarat_crops
from modules.smart_irrigation       import (
    calculate_irrigation_recommendation,
    load_irrigation_rules,
    load_crop_water_requirements,
    get_crop_irrigation_rule,
    save_irrigation_history,
    get_irrigation_history,
    generate_farmer_advice,
)
from modules.whatsapp_alerts        import (
    subscribe, stop_alert, get_stats,
    get_all_subscribers, ALERT_CROPS,
    send_welcome_message, send_whatsapp_message,
)
from modules.email_alerts           import (
    send_irrigation_email,
    get_email_alert_logs,
)

# ── Flask app config ─────────────────────────────────────────────
app = Flask(__name__)

with open(os.path.join(BASE_DIR, "config.json")) as f:
    _cfg = json.load(f)

app.secret_key = _cfg.get("app_secret_key", "agri_secret_2024")

UPLOAD_FOLDER  = os.path.join(BASE_DIR, "static", "images", "uploads")
ALLOWED_EXT    = {"png", "jpg", "jpeg", "webp"}
MAX_UPLOAD_MB  = 10

app.config["UPLOAD_FOLDER"]    = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Context processor: inject today's date everywhere ────────────
@app.context_processor
def inject_globals():
    return {
        "today":      datetime.now().strftime("%d %B %Y"),
        "year":       datetime.now().year,
        "app_name":   "Smart Agriculture System",
    }


# ═══════════════════════════════════════════════════════════════
# 1. DASHBOARD
# ═══════════════════════════════════════════════════════════════
@app.route("/")
def index():
    city    = _cfg.get("default_city", "Ahmedabad")
    weather_result = get_weather(city)
    w       = weather_result.get("weather", {}) if weather_result.get("success") else {}
    adv     = weather_result.get("advisory", {}) if weather_result.get("success") else {}
    return render_template("index.html", weather=w, advisory=adv, city=city)


# ═══════════════════════════════════════════════════════════════
# 2. CROP RECOMMENDATION
# ═══════════════════════════════════════════════════════════════
@app.route("/crop", methods=["GET", "POST"])
def crop():
    result = None
    if request.method == "POST":
        try:
            result = get_top_recommendations(
                N                    = float(request.form["nitrogen"]),
                P                    = float(request.form["phosphorus"]),
                K                    = float(request.form["potassium"]),
                ph                   = float(request.form["ph"]),
                rainfall             = float(request.form["rainfall"]),
                season               = request.form["season"],
                soil_type            = request.form["soil_type"],
                organic_carbon       = float(request.form.get("organic_carbon", 0.5)),
                sand_pct             = float(request.form.get("sand_pct", 33)),
                silt_pct             = float(request.form.get("silt_pct", 33)),
                clay_pct             = float(request.form.get("clay_pct", 34)),
                irrigation_available = request.form.get("irrigation_available", "Yes"),
                water_source         = request.form.get("water_source", "Borewell"),
                water_availability   = request.form.get("water_availability", "Medium"),
                irrigation_type      = request.form.get("irrigation_type", "Flood"),
                water_salinity       = request.form.get("water_salinity", "Normal"),
            )
        except (ValueError, KeyError) as e:
            result = {"success": False, "error": f"Invalid input: {str(e)}"}
    return render_template("crop.html", result=result)


# ═══════════════════════════════════════════════════════════════
# 3. DISEASE DETECTION
# ═══════════════════════════════════════════════════════════════
@app.route("/disease", methods=["GET", "POST"])
def disease():
    result    = None
    img_path  = None

    if request.method == "POST":
        if "leaf_image" not in request.files:
            flash("Please select an image file.", "danger")
            return render_template("disease.html", result=None)

        file = request.files["leaf_image"]
        if file.filename == "":
            flash("No file selected.", "danger")
            return render_template("disease.html", result=None)

        if not allowed_file(file.filename):
            flash("Only PNG, JPG, JPEG, WEBP files are supported.", "warning")
            return render_template("disease.html", result=None)

        filename = secure_filename(
            f"leaf_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        )
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        img_path  = f"images/uploads/{filename}"

        result = detect_disease(save_path)

    return render_template("disease.html", result=result, img_path=img_path)


# ═══════════════════════════════════════════════════════════════
# 4. FERTILIZER — REMOVED (redirect to crop page)
# ═══════════════════════════════════════════════════════════════
@app.route("/fertilizer")
@app.route("/fertilizer/", methods=["GET", "POST"])
def fertilizer():
    return redirect(url_for("crop"))


# ═══════════════════════════════════════════════════════════════
# 5. WEATHER ADVISORY
# ═══════════════════════════════════════════════════════════════
@app.route("/weather", methods=["GET", "POST"])
def weather():
    city     = request.form.get("city", _cfg.get("default_city", "Ahmedabad")) \
               if request.method == "POST" else _cfg.get("default_city", "Ahmedabad")
    pincode  = request.form.get("pincode", "").strip() if request.method == "POST" else ""
    crop     = ""
    result   = get_weather(city, crop, pincode)
    # use city returned by API for forecast (handles pincode → city name mapping)
    forecast_city = result.get("weather", {}).get("city", city) if result.get("success") else city
    forecast = get_forecast(forecast_city, pincode) if result.get("success") else {}
    return render_template("weather.html", result=result,
                           forecast=forecast, city=city, pincode=pincode, crop=crop)


# ── AJAX endpoint for live weather refresh ───────────────────────
@app.route("/api/weather/<city>")
def api_weather(city):
    return jsonify(get_weather(city))


# ═══════════════════════════════════════════════════════════════
# 6. SMART IRRIGATION & WATER MANAGEMENT
# ═══════════════════════════════════════════════════════════════
@app.route("/irrigation", methods=["GET", "POST"])
@app.route("/irrigation/", methods=["GET", "POST"])
def irrigation():
    rules_data   = load_irrigation_rules()
    crops_config = rules_data.get("crops", {})
    crop_list    = list(crops_config.keys())

    # Default / requested parameters
    city         = request.values.get("city", _cfg.get("default_city", "Ahmedabad"))
    crop         = request.values.get("crop", "Cotton")
    growth_stage = request.values.get("growth_stage", request.values.get("stage", "Vegetative"))
    land_area    = float(request.values.get("land_area", request.values.get("area", 2.0)))
    soil_type    = request.values.get("soil_type", request.values.get("soil", "Black"))
    soil_moisture= float(request.values.get("soil_moisture", request.values.get("moisture", 45.0)))
    soil_ph      = float(request.values.get("soil_ph", request.values.get("ph", 7.0)))
    method       = request.values.get("irrigation_method", request.values.get("method", "Drip"))
    water_avail  = request.values.get("water_availability", request.values.get("water_avail", "Medium"))
    last_irrig   = request.values.get("last_irrigation_date", request.values.get("last_irrig", ""))

    # Retrieve live weather data for Gujarat city (reuses weather advisory module)
    weather_res  = get_weather(city)
    weather_info = weather_res.get("weather", {}) if weather_res.get("success") else {}
    forecast_res = get_forecast(city)
    forecast_list= forecast_res.get("forecast", []) if forecast_res.get("success") else []

    # Weather variables with fallback to live API / default
    try:
        weather_temp = float(request.values.get("weather_temp", weather_info.get("temp", 34)))
    except (ValueError, TypeError):
        weather_temp = 34.0

    try:
        weather_hum  = float(request.values.get("weather_humidity", weather_info.get("humidity", 55)))
    except (ValueError, TypeError):
        weather_hum  = 55.0

    today_forecast = forecast_list[0] if forecast_list else {}
    try:
        rain_prob    = float(request.values.get("rain_prob", today_forecast.get("rain_chance", 15)))
    except (ValueError, TypeError):
        rain_prob    = 15.0

    try:
        exp_rain     = float(request.values.get("expected_rainfall", today_forecast.get("rain_mm", 0.0)))
    except (ValueError, TypeError):
        exp_rain     = 0.0

    try:
        wind_speed   = float(request.values.get("wind_speed", weather_info.get("wind_speed", 4.2)))
    except (ValueError, TypeError):
        wind_speed   = 4.2

    result = None

    # On POST (or if explicit calculation requested)
    if request.method == "POST" or request.args.get("analyze") == "1":
        try:
            result = calculate_irrigation_recommendation(
                crop                 = crop,
                growth_stage         = growth_stage,
                land_area            = land_area,
                soil_type            = soil_type,
                soil_moisture        = soil_moisture,
                soil_ph              = soil_ph,
                irrigation_method    = method,
                water_availability   = water_avail,
                last_irrigation_date = last_irrig,
                weather_temp         = weather_temp,
                weather_humidity     = weather_hum,
                rain_prob            = rain_prob,
                expected_rainfall    = exp_rain,
                wind_speed           = wind_speed,
            )
            # Save to temporary JSON history
            save_irrigation_history(result)
        except Exception as e:
            result = {"success": False, "error": f"Calculation error: {str(e)}"}

    history = get_irrigation_history(10)

    # Current form values bundle
    form_values = {
        "city": city,
        "crop": crop,
        "growth_stage": growth_stage,
        "land_area": land_area,
        "soil_type": soil_type,
        "soil_moisture": soil_moisture,
        "soil_ph": soil_ph,
        "irrigation_method": method,
        "water_availability": water_avail,
        "last_irrigation_date": last_irrig,
        "weather_temp": weather_temp,
        "weather_humidity": weather_hum,
        "rain_prob": rain_prob,
        "expected_rainfall": exp_rain,
        "wind_speed": wind_speed,
    }

    return render_template(
        "irrigation.html",
        result=result,
        history=history,
        crops_config=crops_config,
        crop_list=crop_list,
        cities=GUJARAT_CITIES,
        weather=weather_info,
        forecast=forecast_list,
        form_values=form_values,
        rules_data=rules_data,
    )


# ── AJAX API endpoint: Calculate Irrigation Recommendation ────────
@app.route("/api/irrigation/calculate", methods=["POST"])
def api_irrigation_calculate():
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        crop          = data.get("crop", "Cotton")
        stage         = data.get("growth_stage", data.get("stage", "Vegetative"))
        area          = float(data.get("land_area", data.get("area", 1.0)))
        soil_type     = data.get("soil_type", data.get("soil", "Loamy"))
        moisture      = float(data.get("soil_moisture", data.get("moisture", 50.0)))
        ph            = float(data.get("soil_ph", data.get("ph", 7.0)))
        method        = data.get("irrigation_method", data.get("method", "Drip"))
        water_avail   = data.get("water_availability", data.get("water_avail", "Medium"))
        last_date     = data.get("last_irrigation_date", data.get("last_irrig", ""))
        temp          = float(data.get("weather_temp", 32.0))
        hum           = float(data.get("weather_humidity", 55.0))
        rain_prob     = float(data.get("rain_prob", 10.0))
        exp_rain      = float(data.get("expected_rainfall", 0.0))
        wind_speed    = float(data.get("wind_speed", 3.5))

        rec = calculate_irrigation_recommendation(
            crop                 = crop,
            growth_stage         = stage,
            land_area            = area,
            soil_type            = soil_type,
            soil_moisture        = moisture,
            soil_ph              = ph,
            irrigation_method    = method,
            water_availability   = water_avail,
            last_irrigation_date = last_date,
            weather_temp         = temp,
            weather_humidity     = hum,
            rain_prob            = rain_prob,
            expected_rainfall    = exp_rain,
            wind_speed           = wind_speed,
        )
        save_irrigation_history(rec)
        return jsonify(rec)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ── AJAX API endpoint: Get Crop Rules & Config ───────────────────
@app.route("/api/irrigation/crop-rules/<crop>", methods=["GET"])
def api_irrigation_crop_rule(crop):
    rule = get_crop_irrigation_rule(crop)
    return jsonify({"success": True, "crop": crop, "rule": rule})


# ── AJAX API endpoint: List all Crops ─────────────────────────────
@app.route("/api/irrigation/crops", methods=["GET"])
def api_irrigation_crops():
    rules = load_irrigation_rules()
    return jsonify({"success": True, "crops": rules.get("crops", {})})


# ── AJAX API endpoint: Irrigation History ─────────────────────────
@app.route("/api/irrigation/history", methods=["GET", "DELETE"])
def api_irrigation_history():
    if request.method == "DELETE":
        try:
            history_file = os.path.join(BASE_DIR, "data", "user_history.json")
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    h = json.load(f)
                h["irrigation_logs"] = []
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump(h, f, indent=2, ensure_ascii=False)
            return jsonify({"success": True, "message": "Irrigation history cleared."})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    return jsonify({"success": True, "history": get_irrigation_history(20)})


# ── AJAX API endpoint: Send Irrigation Email Alert ───────────────
@app.route("/api/irrigation/send-email", methods=["POST"])
def api_irrigation_send_email():
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        email = data.get("email", "").strip()
        alert_data = data.get("alert_data", {})
        if not alert_data and "crop" in data:
            alert_data = data

        if not email:
            return jsonify({"success": False, "error": "Please enter a valid email address."}), 400

        resp = send_irrigation_email(email, alert_data)
        return jsonify(resp)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── AJAX API endpoint: Get Sent Email Logs ────────────────────────
@app.route("/api/irrigation/email-logs", methods=["GET"])
def api_irrigation_email_logs():
    return jsonify({"success": True, "logs": get_email_alert_logs(20)})


# ── AJAX API endpoint: Send Instant Irrigation WhatsApp Alert ─────
@app.route("/api/irrigation/send-alert", methods=["POST"])
def api_irrigation_send_alert():
    try:
        data   = request.get_json(silent=True) or request.form.to_dict()
        number = data.get("whatsapp_number", "").strip()
        alert_msg = data.get("alert_text", "").strip()
        if not number:
            return jsonify({"success": False, "error": "Please enter a valid WhatsApp mobile number."})
        if not alert_msg:
            return jsonify({"success": False, "error": "No alert message payload."})

        resp = send_whatsapp_message(number, alert_msg)
        return jsonify(resp)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# ═══════════════════════════════════════════════════════════════
# 7. MARKET PRICES
# ═══════════════════════════════════════════════════════════════
@app.route("/market", methods=["GET", "POST"])
def market():
    result   = None
    crop     = request.form.get("crop", "Wheat")   if request.method == "POST" else "Wheat"
    state    = request.form.get("state", _cfg.get("default_state", "Gujarat")) \
               if request.method == "POST" else _cfg.get("default_state", "Gujarat")

    if request.method == "POST":
        result = get_market_prices(crop, state)

    alert_stats = get_stats()
    return render_template("market.html", result=result, crop=crop, state=state,
                           alert_crops=ALERT_CROPS, alert_stats=alert_stats)


# ── AJAX endpoint for market price fetch ────────────────────────
@app.route("/api/market/<crop>/<state>")
def api_market(crop, state):
    return jsonify(get_market_prices(crop, state))


# ═══════════════════════════════════════════════════════════════
# 7b. WHATSAPP ALERT ROUTES
# ═══════════════════════════════════════════════════════════════
@app.route("/alerts/subscribe", methods=["POST"])
def alert_subscribe():
    number = request.form.get("whatsapp_number", "").strip()
    crop   = request.form.get("alert_crop", "").strip()
    if not number or not crop:
        return jsonify({"success": False, "error": "Please enter WhatsApp number and select a crop."})
    result = subscribe(number, crop)
    return jsonify(result)


@app.route("/alerts/stop", methods=["POST"])
def alert_stop():
    number = request.form.get("whatsapp_number", "").strip()
    if not number:
        return jsonify({"success": False, "error": "Please enter your WhatsApp number."})
    result = stop_alert(number)
    return jsonify(result)


@app.route("/alerts/stats")
def alert_stats_api():
    return jsonify(get_stats())


@app.route("/alerts/send-now", methods=["POST"])
def alert_send_now():
    """Manual trigger for daily alerts (admin use / testing)."""
    try:
        from modules.send_daily_alerts import run_daily_alerts
        log = run_daily_alerts()
        return jsonify({"success": True, "log": log})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════════
# 8. SOLAR — REMOVED (redirect to home)
# ═══════════════════════════════════════════════════════════════
@app.route("/solar")
@app.route("/solar/", methods=["GET", "POST"])
def solar():
    return redirect(url_for("index"))


# ═══════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404

@app.errorhandler(413)
def too_large(e):
    flash(f"Image too large. Max size is {MAX_UPLOAD_MB}MB.", "danger")
    return redirect(url_for("disease"))


# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("=" * 55)
    print("  * Smart Agriculture System Starting...")
    print(f"  * Base Directory: {BASE_DIR}")
    print("  * Open: http://localhost:5000")
    print("=" * 55)
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)

