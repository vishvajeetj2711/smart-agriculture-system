# CHAPTER 5 — IMPLEMENTATION

---

## 5.1   Implementation Platform / Environment

| Component | Details |
|---|---|
| Operating System | Windows 10/11 or Linux Ubuntu 20.04+ |
| Programming Language | Python 3.12.10 |
| Web Framework | Flask 3.1.3 |
| ML Framework | scikit-learn 1.9.1, TensorFlow 2.13 |
| Data Processing | NumPy 2.4.6, Pandas 3.0.6 |
| Image Processing | Pillow 11.3.0, OpenCV 4.8 |
| Frontend | HTML5, Bootstrap 5.3, Chart.js 4.x, JavaScript ES6 |
| Development IDE | Visual Studio Code / Kiro IDE |
| Data Storage | JSON files (no database) |
| Server | Flask Development Server (port 5000) |

---

## 5.2   Project Directory Structure

```
Smart Agricultural System/
├── app.py                          # Main Flask application
├── config.json                     # API keys and configuration
├── requirements.txt                # Python dependencies
│
├── modules/
│   ├── crop_recommendation.py      # Random Forest + rule-based crop engine
│   ├── disease_detection.py        # MobileNetV2 CNN disease detection
│   ├── weather_advisory.py         # OpenWeatherMap API + bilingual advisory
│   ├── smart_irrigation.py         # Deterministic irrigation decision engine
│   ├── market_prices.py            # Agmarknet API + price trend + sell advice
│   ├── whatsapp_alerts.py          # Meta Cloud API WhatsApp messaging
│   ├── email_alerts.py             # SMTP email alert module
│   ├── fertilizer_recommendation.py# Fertilizer Random Forest module
│   ├── solar_estimator.py          # Solar income calculator
│   └── __init__.py
│
├── models/
│   ├── crop_model.pkl              # Trained Random Forest model
│   ├── crop_label_encoder.pkl      # Label encoder for crop classes
│   ├── fertilizer_model.pkl        # Trained fertilizer model
│   ├── disease_model.h5            # MobileNetV2 Keras model
│   └── train_models.py             # Model training script
│
├── data/
│   ├── crops.json                  # Crop database (25+ crops)
│   ├── diseases.json               # Disease database (38 classes)
│   ├── irrigation.json             # Crop irrigation rules and factors
│   ├── fertilizers.json            # Fertilizer database
│   ├── user_history.json           # Query history logs
│   ├── market_cache.json           # Mandi price cache
│   ├── weather_log.json            # Weather query logs
│   ├── price_history.json          # Price history for trend charts
│   ├── whatsapp_alerts.json        # Subscriber database
│   ├── email_alerts.json           # Sent email log
│   └── solar_records.json          # Solar calculation history
│
├── static/
│   ├── css/style.css               # Custom styles
│   ├── js/main.js                  # Frontend JavaScript
│   ├── js/lang.js                  # Language/translation utilities
│   └── images/uploads/             # Uploaded leaf images
│
└── templates/
    ├── base.html                   # Base template with navbar/footer
    ├── index.html                  # Dashboard
    ├── crop.html                   # Crop recommendation page
    ├── disease.html                # Disease detection page
    ├── irrigation.html             # Smart irrigation page
    ├── weather.html                # Weather advisory page
    └── market.html                 # Market prices page
```

---

## 5.3   Module Implementation Details

### 5.3.1   Flask Application (app.py)

The main Flask application (`app.py`) serves as the integration hub for all modules. It defines routes for each feature page and corresponding AJAX API endpoints.

Key implementation highlights:
- `app.secret_key` is loaded from `config.json` for session security.
- Upload folder is auto-created using `os.makedirs(UPLOAD_FOLDER, exist_ok=True)`.
- A context processor (`inject_globals`) injects `today`, `year`, and `app_name` into every template automatically.
- `MAX_CONTENT_LENGTH` is set to 10MB to prevent oversized file uploads.

**Key Routes:**

```python
@app.route("/")                  # Dashboard with live weather
@app.route("/crop")              # Crop recommendation (GET/POST)
@app.route("/disease")           # Disease detection (GET/POST with file upload)
@app.route("/irrigation")        # Smart irrigation (GET/POST)
@app.route("/weather")           # Weather advisory (GET/POST)
@app.route("/market")            # Market prices (GET/POST)
@app.route("/api/irrigation/calculate")    # AJAX: Irrigation calculation
@app.route("/api/irrigation/send-email")   # AJAX: Send email alert
@app.route("/api/irrigation/send-alert")   # AJAX: Send WhatsApp alert
@app.route("/api/market/<crop>/<state>")   # AJAX: Market price fetch
@app.route("/api/weather/<city>")          # AJAX: Weather refresh
```

---

### 5.3.2   Crop Recommendation Implementation

The `get_top_recommendations()` function in `crop_recommendation.py` handles crop suggestion:

```python
def get_top_recommendations(N, P, K, ph, rainfall, season, soil_type,
                             organic_carbon, sand_pct, silt_pct, clay_pct,
                             irrigation_available, water_source,
                             water_availability, irrigation_type,
                             water_salinity, top_n=3):

    model, le = _load_model()       # Load RandomForest + LabelEncoder
    crops_data = _load_crops()      # Load crops.json database

    # Season → temperature/humidity inference for Gujarat
    season_temp = {"Kharif": 30, "Rabi": 18, "Zaid": 35, "Annual": 27}
    season_hum  = {"Kharif": 70, "Rabi": 55, "Zaid": 40, "Annual": 60}

    if model:
        # ML Model Path
        features = [N, P, K, temperature, humidity, ph, rainfall,
                    season_enc, soil_enc]
        proba = model.predict_proba([features])[0]
        top_indices = argsort(proba)[::-1][:top_n]
        # Return crop names + confidence percentages

    else:
        # Rule-Based Fallback (15+ parameters)
        scores = []
        for crop in crops_data:
            score = (season_match + soil_match + ph_match +
                     rainfall_match + water_score + organic_bonus +
                     texture_bonus + salinity_bonus)
            scores.append((crop, score))
        return top-3 by score
```

The rule-based engine scores each crop on 8 criteria with weighted points (total possible: ~100 points), ensuring meaningful recommendations even without a trained model.

---

### 5.3.3   Disease Detection Implementation

The `detect_disease()` function in `disease_detection.py` processes leaf images:

```python
def detect_disease(image_path):
    # Step 1: Load MobileNetV2 model
    model = tf.keras.models.load_model(MODEL_PATH)

    # Step 2: Preprocess image
    img = PIL.Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = arr / 127.5 - 1.0          # MobileNetV2 normalization [-1, 1]
    batch = np.expand_dims(arr, 0)   # Shape: (1, 224, 224, 3)

    # Step 3: Predict
    preds = model.predict(batch)[0]
    top_idx = np.argsort(preds)[::-1][:3]
    predicted_class = top_idx[0]
    confidence = preds[top_idx[0]] * 100

    # Step 4: Look up disease information from diseases.json
    disease_info = diseases[predicted_class]

    return {
        "disease_name", "symptoms", "treatment", "prevention",
        "severity", "confidence", "top_predictions"
    }
```

In demo mode (when `disease_model.h5` is absent), the system randomly selects a disease from `diseases.json` with a simulated confidence of 72–96%, clearly marking the result as demo data.

---

### 5.3.4   Smart Irrigation Implementation

The `calculate_irrigation_recommendation()` function in `smart_irrigation.py` implements the 5-rule decision engine:

```python
def calculate_irrigation_recommendation(crop, growth_stage, land_area,
                                         soil_type, soil_moisture, soil_ph,
                                         irrigation_method, water_availability,
                                         last_irrigation_date, weather_temp,
                                         weather_humidity, rain_prob,
                                         expected_rainfall, wind_speed):

    crop_rule = get_crop_irrigation_rule(crop)
    critical_moist = crop_rule["criticalMoisture"]
    minimum_moist  = crop_rule["minimumMoisture"]
    ideal_min      = crop_rule["idealMoistureMin"]
    ideal_max      = crop_rule["idealMoistureMax"]

    # Apply Rules in priority order
    if evaluate_rainfall_risk(rain_prob, expected_rainfall):
        status = "WAIT"             # Rule A
    elif soil_moisture >= 80 or soil_moisture > ideal_max:
        status = "NO_IRRIGATION"    # Rule E
    elif soil_moisture <= critical_moist:
        status = "HIGH"             # Rule B
    elif soil_moisture < minimum_moist:
        status = "MEDIUM"           # Rule C
    elif ideal_min <= soil_moisture <= ideal_max:
        status = "LOW"              # Rule D

    # Water volume calculation
    water_calc = calculate_water_requirement(...)
    estimated_water_L = water_calc["applied_water_L"] if irrigation_required else 0

    # Generate bilingual farmer advice
    farmer_advice = generate_farmer_advice(status, crop, soil_moisture, ...)

    return {status, estimated_water_L, recommended_time,
            farmer_advice (EN+GU), alert_text, technical_details}
```

---

### 5.3.5   Weather Advisory Implementation

The `get_weather()` function in `weather_advisory.py` fetches and processes weather data:

```python
def get_weather(city, crop="", pincode=""):
    # Support both city name and pincode search
    if pincode and pincode.isdigit():
        params = {"zip": f"{pincode},IN", "appid": api_key, "units": "metric"}
    else:
        params = {"q": f"{city},IN", "appid": api_key, "units": "metric"}

    resp = requests.get(OWM_URL + "/weather", params=params, timeout=10)
    data = resp.json()

    # Parse response into clean weather dict
    weather = {temp, feels_like, humidity, wind_speed, description, ...}

    # Generate advisory based on weather values
    advisory = _generate_advisory(weather)
    # Returns: irrigation_status, pest_risk_level, farm_tip
```

The `get_forecast()` function aggregates 5-day/3-hour API data into a 7-day daily summary, with intelligent padding for the remaining days using deterministic random seeds (ensuring consistent display).

---

### 5.3.6   Email and WhatsApp Alert Implementation

**Email Module (`email_alerts.py`):**
- Builds a rich HTML email with inline CSS for maximum email client compatibility.
- Supports both live SMTP sending and demo mode logging.
- Demo mode saves alert details to `email_alerts.json` without actually sending.
- In live mode, uses Python `smtplib` with STARTTLS encryption for Gmail SMTP.

**WhatsApp Module (`whatsapp_alerts.py`):**
- Normalizes Indian phone numbers to E.164 format (`+91XXXXXXXXXX`).
- Calls Meta WhatsApp Cloud API `/{phone_id}/messages` endpoint.
- Supports subscribe, update crop, and stop alert operations.
- In demo mode, prints message preview to console and logs to JSON.

---

### 5.3.7   How to Run the Project

**Step 1: Install Dependencies**
```
pip install -r requirements.txt
```

**Step 2: Configure API Keys (optional)**
```
Edit config.json:
- openweathermap_api_key: Get from openweathermap.org
- agmarknet_api_key: Get from data.gov.in
- whatsapp_api_token: Get from developers.facebook.com
- smtp_username / smtp_password: Gmail app password
```

**Step 3: Run the Application**
```
python app.py
```

**Step 4: Open in Browser**
```
http://localhost:5000
```

The system runs fully in demo mode without any API keys configured.

---

## 5.4   Finding / Results / Outcomes

The implemented Smart Agricultural System successfully delivers the following outcomes:

1. **Crop Recommendation:** Returns top-3 crop suggestions with confidence percentages, season information, water requirement, and crop descriptions for all 25+ Gujarat crops.
2. **Disease Detection:** Returns disease diagnosis with confidence score, symptoms, treatment, and prevention advice. In demo mode, demonstrates the complete UI flow.
3. **Smart Irrigation:** Accurately applies the 5-rule decision engine and calculates water volumes in litres with bilingual advice. The alert text can be directly sent via WhatsApp.
4. **Weather Advisory:** Displays real-time weather from OpenWeatherMap with 3-panel advisory (irrigation + pest risk + farm tip) and a 7-day forecast.
5. **Market Prices:** Shows Gujarat mandi prices in a sortable table with a 7-day Chart.js line chart and actionable sell/wait recommendation.
6. **Alert Systems:** WhatsApp and email alerts work in demo mode with full message preview; production alerts function when API credentials are configured.

---

## 5.5   Result Analysis

| Module | Demo Mode Output | Live Mode Output |
|---|---|---|
| Crop Recommendation | Rule-based scoring (0–100) | Random Forest probability (0–100%) |
| Disease Detection | Random disease selection (72–96% conf) | CNN model prediction (actual %) |
| Irrigation | Full calculation with all rules | Same (no API dependency) |
| Weather | Pre-configured Ahmedabad data | Live OWM API data |
| Market Prices | MSP-based generated prices | Live Agmarknet data |
| WhatsApp Alert | Console log + JSON save | Meta API message delivery |
| Email Alert | Subject + HTML preview | Actual SMTP delivery |

---

## 5.6   Summary

This chapter described the complete implementation of the Smart Agricultural System, covering the technology environment, directory structure, and detailed implementation of each module with code snippets. The system successfully integrates all six modules into a unified, functional web application accessible at `http://localhost:5000`.

---
