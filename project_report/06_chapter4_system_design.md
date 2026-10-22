# CHAPTER 4 — SYSTEM DESIGN

---

## 4.1   System Architecture

The Smart Agricultural System follows a **modular, layered architecture** organized into four layers:

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                    │
│   HTML5 + Bootstrap 5 + JavaScript + Chart.js           │
│   Templates: index.html, crop.html, disease.html,       │
│              irrigation.html, weather.html, market.html │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP Requests / JSON Responses
┌───────────────────────▼─────────────────────────────────┐
│                   APPLICATION LAYER                     │
│   Flask Web Framework (app.py)                          │
│   Routes: /, /crop, /disease, /irrigation,              │
│            /weather, /market, /api/*                    │
└───────────────────────┬─────────────────────────────────┘
                        │ Function Calls
┌───────────────────────▼─────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                  │
│   modules/crop_recommendation.py                        │
│   modules/disease_detection.py                          │
│   modules/weather_advisory.py                           │
│   modules/smart_irrigation.py                           │
│   modules/market_prices.py                              │
│   modules/whatsapp_alerts.py                            │
│   modules/email_alerts.py                               │
│   modules/fertilizer_recommendation.py                  │
│   modules/solar_estimator.py                            │
└───────────────────────┬─────────────────────────────────┘
                        │ Read / Write
┌───────────────────────▼─────────────────────────────────┐
│                   DATA LAYER                            │
│   data/crops.json           data/diseases.json          │
│   data/irrigation.json      data/fertilizers.json       │
│   data/user_history.json    data/market_cache.json      │
│   data/weather_log.json     data/price_history.json     │
│   data/whatsapp_alerts.json data/email_alerts.json      │
│   models/crop_model.pkl     models/disease_model.h5     │
└─────────────────────────────────────────────────────────┘
                        │ REST API Calls
┌───────────────────────▼─────────────────────────────────┐
│               EXTERNAL SERVICES LAYER                   │
│   OpenWeatherMap API      Agmarknet / data.gov.in API   │
│   Meta WhatsApp Cloud API Gmail SMTP Server             │
└─────────────────────────────────────────────────────────┘
```

---

## 4.2   Module Design

### 4.2.1   Crop Recommendation Module Design

**Inputs:**
- Nitrogen (N), Phosphorus (P), Potassium (K) in mg/kg
- Soil pH (3.0 – 10.0)
- Annual Rainfall (mm)
- Season (Kharif / Rabi / Zaid / Annual)
- Soil Type (Clayey / Loamy / Sandy Loam / Black / Red / Alluvial)
- Organic Carbon (%)
- Soil Texture: Sand %, Silt %, Clay %
- Irrigation Available (Yes/No), Water Source, Water Availability, Irrigation Type, Water Salinity

**Processing:**
```
IF trained model (crop_model.pkl) EXISTS:
    Encode season and soil type to numeric values
    Build feature vector: [N, P, K, temp, humidity, pH, rainfall, season_enc, soil_enc]
    Apply Random Forest model → get probability array
    Return top-3 crops by probability
ELSE (model not available):
    Apply rule-based scoring engine:
        Score each crop by:
        + Season match (30 pts)
        + Soil type match (18 pts)
        + pH suitability (14 pts)
        + Rainfall match (14 pts)
        + Water requirement vs availability (14 pts)
        + Organic carbon bonus (6 pts)
        + Soil texture suitability (8 pts)
        + Irrigation type & salinity bonuses (4–6 pts)
    Return top-3 crops by total score
```

**Outputs:** Top-3 crops with confidence %, season, water requirement, description, icon.

---

### 4.2.2   Disease Detection Module Design

**Inputs:** Leaf image file (PNG/JPG/JPEG/WEBP, max 10MB)

**Processing:**
```
IF disease_model.h5 EXISTS:
    Load image → Resize to 224×224 px
    Normalize: pixel_value / 127.5 - 1.0  (MobileNetV2 preprocessing)
    Add batch dimension → shape (1, 224, 224, 3)
    model.predict() → probability array for 38 disease classes
    Get top-3 predictions by probability
ELSE (model not available — Demo Mode):
    Select random disease from diseases.json
    Generate realistic confidence score (72–96%)
    Return top-3 with simulated probabilities
```

**Outputs:** Disease name, crop, pathogen, symptoms, treatment, prevention, severity, confidence, top-3 predictions, model used.

---

### 4.2.3   Smart Irrigation Decision Rules

The irrigation module applies **5 deterministic rules** in priority order:

```
Rule A (Highest Priority) — Expected Rainfall:
    IF rain_probability >= 70% AND expected_rainfall >= 5mm  → STATUS: WAIT
    IF rain_probability >= 80% AND expected_rainfall >= 2mm  → STATUS: WAIT
    IF rain_probability >= 85%                               → STATUS: WAIT

Rule E — Soil Saturation:
    IF soil_moisture > ideal_max (crop-specific) OR >= 80%   → STATUS: NO_IRRIGATION

Rule B — Critical Moisture:
    IF soil_moisture <= critical_moisture (crop-specific)    → STATUS: HIGH (Irrigate Immediately)

Rule C — Below Minimum:
    IF soil_moisture < minimum_moisture (crop-specific)      → STATUS: MEDIUM (Plan Irrigation)

Rule D (Lowest Priority) — Ideal Range:
    IF ideal_min <= soil_moisture <= ideal_max               → STATUS: LOW (No Action)

Adjusted Rule:
    IF minimum <= soil_moisture < ideal_min AND temp > 35°C  → STATUS: MEDIUM
```

**Water Volume Calculation Formula:**

```
Applied Water (L) =
  [Land Area × Base Water/Acre × Stage Factor × Moisture Deficit Ratio
    × Soil Factor × Water Availability Factor - Rain Offset (L)]
  ÷ Irrigation Method Efficiency

Where:
  Rain Offset (L) = Expected Rainfall (mm) × 4046.86 × Land Area (Acres)
  Irrigation Method Efficiency: Drip=0.90, Sprinkler=0.75, Flood=0.60, Furrow=0.65
```

---

### 4.2.4   Weather Advisory Module Design

```
Input: City name or Pincode

Step 1: Call OpenWeatherMap /weather endpoint
Step 2: Call OpenWeatherMap /forecast endpoint (5-day/3-hour data)
Step 3: Parse response → extract temp, humidity, wind, rain, description
Step 4: Generate Advisory:
    - Irrigation Status: based on rain_1h, humidity, temp
    - Pest Risk Level: based on humidity + temp combination
    - Farm Tip: based on weather description + temperature
Step 5: Aggregate 5-day/3-hour data into daily 7-day forecast
Step 6: Save to weather_log.json and user_history.json

Output: weather object + advisory object + 7-day forecast list
```

---

### 4.2.5   Market Price Module Design

```
Input: Crop name + Gujarat District

Step 1: Check market_cache.json (TTL: 3 hours)
    IF cache valid → return cached prices
    
Step 2: IF Agmarknet API key configured:
    Call data.gov.in API with crop + state=Gujarat + district
    Parse records → build price list
    ELSE (demo mode):
    Generate realistic mandi prices using base MSP values
    Apply random variation (±10–15%) per mandi

Step 3: Sort by modal_price (descending)
Step 4: Generate 7-day price trend (random seed by crop+date for consistency)
Step 5: Generate Sell/Wait advice:
    IF price < MSP → Advise MSP procurement
    IF trend Rising > 5% → Advise Wait
    IF trend Falling > 5% → Advise Sell Now
    IF price > avg × 1.08 → Advise Sell at Best Market
Step 6: Save to cache and price_history.json

Output: prices list + trend data + sell advice + MSP info
```

---

## 4.3   Data Structure Design

### 4.3.1   crops.json Structure

```json
{
  "crops": [
    {
      "name": "Cotton",
      "season": ["Kharif"],
      "soil_types": ["Black", "Loamy"],
      "ph_range": [6.0, 8.0],
      "rainfall_mm": [500, 1200],
      "water_requirement": "High",
      "icon": "🌿",
      "description_en": "Cotton is Gujarat's primary cash crop..."
    }
  ]
}
```

### 4.3.2   irrigation.json Structure

```json
{
  "crops": {
    "Cotton": {
      "minimumMoisture": 35,
      "idealMoistureMin": 50,
      "idealMoistureMax": 70,
      "criticalMoisture": 25,
      "baseWaterPerAcre": 22000,
      "preferredIrrigationTime": ["Morning", "Evening"]
    }
  },
  "growthStageFactors": {
    "Seedling": 0.8,
    "Vegetative": 1.0,
    "Flowering": 1.2,
    "Maturity": 0.8
  },
  "irrigationEfficiency": {
    "Drip": 0.90,
    "Sprinkler": 0.75,
    "Flood": 0.60
  }
}
```

### 4.3.3   user_history.json Structure

```json
{
  "crop_recommendations": [],
  "disease_detections": [],
  "weather_queries": [],
  "irrigation_logs": [],
  "market_queries": [],
  "fertilizer_recommendations": [],
  "solar_estimates": []
}
```

---

## 4.4   Input / Output and Interface Design

### 4.4.1   Dashboard (index.html)

- **Input:** None (auto-loads weather for default city: Ahmedabad)
- **Output:** Live weather card, quick access navigation to all modules

### 4.4.2   Crop Recommendation (crop.html)

- **Input Form:** N, P, K, pH, rainfall, season dropdown, soil type dropdown, organic carbon, sand/silt/clay sliders, irrigation options
- **Output:** 3 crop recommendation cards with confidence bars, description, water requirement badge

### 4.4.3   Disease Detection (disease.html)

- **Input Form:** Image file upload (drag-and-drop or browse)
- **Output:** Disease diagnosis card with image preview, confidence gauge, symptoms/treatment/prevention accordion

### 4.4.4   Smart Irrigation (irrigation.html)

- **Input Form:** Crop, growth stage, area (acres), soil type, soil moisture slider, soil pH, irrigation method, water availability, last irrigation date, city, weather parameters
- **Output:** Status badge (HIGH/MEDIUM/LOW/WAIT/NO_IRRIGATION), estimated water volume, recommended time, bilingual farmer advice, email/WhatsApp alert buttons, history table

### 4.4.5   Weather Advisory (weather.html)

- **Input Form:** City dropdown (20 Gujarat cities) or pincode
- **Output:** Current weather card, 3-panel advisory (irrigation + pest risk + farm tip), 7-day forecast cards

### 4.4.6   Market Prices (market.html)

- **Input Form:** Crop dropdown, Gujarat district dropdown
- **Output:** Mandi price table, 7-day trend line chart, sell/wait recommendation card, WhatsApp alert subscription form

---

## 4.5   Security Design

1. **API Key Management:** All API keys (OpenWeatherMap, Agmarknet, WhatsApp, SMTP) are stored in `config.json` and never exposed in HTML or JavaScript.
2. **File Upload Security:** Uploaded images are validated by extension and MIME type. Filenames are sanitized using `werkzeug.utils.secure_filename()`. Maximum upload size is limited to 10MB.
3. **Input Validation:** All numeric form inputs are validated and type-cast with try/except blocks before processing.
4. **Demo Mode Fallback:** When API keys are placeholder values, the system operates in demo mode and never attempts to make live API calls, preventing credential exposure.

---

## 4.6   Summary

This chapter presented the complete system design including the layered architecture, detailed module designs with processing flowcharts, data structure schemas, interface designs, and security considerations. The modular design ensures that each component can be independently maintained, tested, and upgraded.

---
