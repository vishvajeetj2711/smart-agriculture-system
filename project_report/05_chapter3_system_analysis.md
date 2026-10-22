# CHAPTER 3 — SYSTEM ANALYSIS

---

## 3.1   Study of the Current System

Currently, farmers in Gujarat rely on a combination of the following information sources for agricultural decision-making:

1. **Krishi Vigyan Kendras (KVKs):** Government-run agricultural extension centers that provide advice on crop selection and pest management. However, these centers have limited reach, and farmers must physically visit them.
2. **Agricultural Department Helplines:** State government helplines that provide text-based advisories. These are not personalized and lack real-time data.
3. **Neighbours and Intermediaries (Adatiyas):** Most farmers rely heavily on the experience of other farmers or market middlemen, leading to decisions based on anecdote rather than data.
4. **Manual Soil Testing:** Soil testing is available through state laboratories, but results take 2–4 weeks and are not automatically linked to crop or fertilizer recommendations.
5. **Daily Newspapers and TV:** Farmers access market prices and weather forecasts through newspapers and TV, which provide generalized state-level information rather than district or mandi-level data.
6. **Mobile Apps (e.g., Kisan Suvidha, AgroStar):** Some farmers use mobile apps, but these require internet connectivity, are often not available in Gujarati, and do not provide integrated multi-feature advisory.

---

## 3.2   Problems and Weaknesses of the Current System

| # | Problem | Impact |
|---|---|---|
| 1 | Crop selection based on habit, not soil data | Suboptimal yield, soil nutrient depletion |
| 2 | Disease identification done visually by farmers | Late detection, high crop loss |
| 3 | Irrigation based on fixed schedules | Water waste, over/under-irrigation |
| 4 | Market price from middlemen | Farmers get below-market rates |
| 5 | No localized weather-based farm advice | Missed spray windows, drought stress |
| 6 | Fragmented tools (no single platform) | High time cost, low adoption |
| 7 | No Gujarati language support in digital tools | Low adoption by rural farmers |
| 8 | Requires expensive hardware or internet | Not accessible to smallholders |

---

## 3.3   Requirements of the New System

### 3.3.1   Functional Requirements

1. **FR-01:** The system shall accept soil parameters (N, P, K, pH, organic carbon, soil texture, rainfall) and recommend the top 3 suitable crops with confidence scores.
2. **FR-02:** The system shall allow farmers to upload a leaf image and return disease name, pathogen type, symptoms, treatment, and prevention advice.
3. **FR-03:** The system shall calculate irrigation water requirement (in litres) based on soil moisture, crop growth stage, soil type, weather, and irrigation method.
4. **FR-04:** The system shall display current weather conditions and a 7-day forecast for any Gujarat city or pincode.
5. **FR-05:** The system shall fetch Gujarat mandi prices for selected crops and display price trends with sell/wait recommendations.
6. **FR-06:** The system shall allow farmers to subscribe for daily WhatsApp crop price alerts.
7. **FR-07:** The system shall send detailed irrigation advisory reports via email on demand.
8. **FR-08:** The system shall generate bilingual (English + Gujarati) advisories for weather, irrigation, and pest risk.
9. **FR-09:** The system shall operate in demo mode when external API keys are not configured.
10. **FR-10:** The system shall maintain query history logs (crop recommendations, disease detections, weather queries, irrigation logs, market queries) in JSON files.

### 3.3.2   Non-Functional Requirements

1. **NFR-01 (Performance):** The system shall respond to user requests within 3 seconds for all modules except disease detection (which may take up to 8 seconds for model inference).
2. **NFR-02 (Usability):** The interface shall be accessible on both desktop and mobile browsers without requiring additional software installation.
3. **NFR-03 (Reliability):** The system shall fall back to demo/cached mode gracefully when external APIs are unavailable.
4. **NFR-04 (Portability):** The system shall run on any standard Python 3.9+ environment on Windows, Linux, or macOS.
5. **NFR-05 (Security):** API keys and credentials shall be stored in a configuration file, not hardcoded in source code.
6. **NFR-06 (Maintainability):** Each functional module shall be implemented as a separate Python file to allow independent updates.

---

## 3.4   System Feasibility Analysis

### 3.4.1   Technical Feasibility

The system uses Python 3.12, Flask, scikit-learn, TensorFlow/Keras, and standard REST APIs — all of which are mature, well-documented, freely available technologies. The development team has the required Python and web development skills. No specialized hardware is required. The system is technically feasible.

### 3.4.2   Economic Feasibility

- All software tools and libraries are open-source and free of cost.
- OpenWeatherMap API provides a free tier sufficient for development and small-scale use.
- Agmarknet API (data.gov.in) is free for Indian citizens and registered developers.
- Meta WhatsApp Cloud API offers a free tier for testing.
- The only cost involved is a standard web hosting server (approximately ₹300–500/month) for production deployment.
- The system is economically feasible for both development and deployment.

### 3.4.3   Operational Feasibility

- The system is accessed through a standard web browser — no installation required by end users.
- The interface is designed to be simple and intuitive for farmers with basic smartphone literacy.
- Bilingual advisories (English + Gujarati) ensure accessibility for Gujarati-speaking farmers.
- The system is operationally feasible.

---

## 3.5   Activity / Process in the Proposed System

The overall workflow of the Smart Agricultural System is as follows:

```
Farmer visits the web application
          |
          |-----> Dashboard (Live Weather + Quick Access)
          |
          |-----> Crop Recommendation
          |           |
          |           +-- Enter soil params (N, P, K, pH, rainfall, season, soil type,
          |                                  organic carbon, texture, water params)
          |           +-- System applies Random Forest / Rule-Based Engine
          |           +-- Returns Top 3 Crop Recommendations with confidence scores
          |
          |-----> Disease Detection
          |           |
          |           +-- Upload leaf image (JPG/PNG/WEBP)
          |           +-- System preprocesses image (224x224, MobileNetV2 normalization)
          |           +-- CNN Model / Demo mode returns disease, symptoms, treatment
          |
          |-----> Smart Irrigation
          |           |
          |           +-- Select crop, growth stage, area, soil type, moisture, method
          |           +-- System fetches live weather for selected city
          |           +-- Applies Rules A-E (Rainfall → Saturation → Critical → Minimum → Ideal)
          |           +-- Returns water volume (L), irrigation time, bilingual advice
          |           +-- Option to send email / WhatsApp alert
          |
          |-----> Weather Advisory
          |           |
          |           +-- Select Gujarat city or enter pincode
          |           +-- Fetches live weather from OpenWeatherMap API
          |           +-- Generates irrigation + pest risk + farm tip advisories
          |           +-- Displays 7-day forecast
          |
          |-----> Market Prices
          |           |
          |           +-- Select crop + Gujarat district
          |           +-- Fetches Agmarknet API / cache
          |           +-- Shows mandi prices, 7-day trend chart, sell/wait advice
          |           +-- Subscribe to daily WhatsApp price alert
```

---

## 3.6   Features of the Proposed System

1. **Integrated Platform:** All six modules (crop, disease, irrigation, weather, market, alerts) in one application.
2. **AI-Powered:** Machine learning models (Random Forest, MobileNetV2 CNN) for intelligent recommendations.
3. **Real-Time Data:** Live weather and market price integration via external REST APIs.
4. **Bilingual Support:** All advisories available in English and Gujarati.
5. **Offline/Demo Mode:** System remains functional even without API keys.
6. **Lightweight Architecture:** JSON-file storage eliminates database server dependency.
7. **Mobile-Responsive:** Bootstrap 5-based UI works on smartphones and tablets.
8. **Alert Integration:** WhatsApp and Email notifications for irrigation and price advisories.

---

## 3.7   Main Modules / Components of the Proposed System

| Module Name | Python File | Functionality |
|---|---|---|
| Crop Recommendation | crop_recommendation.py | Random Forest + Rule-Based crop suggestion |
| Disease Detection | disease_detection.py | MobileNetV2 CNN leaf image analysis |
| Weather Advisory | weather_advisory.py | OpenWeatherMap API + bilingual advisory |
| Smart Irrigation | smart_irrigation.py | Deterministic rule engine + water calc |
| Market Prices | market_prices.py | Agmarknet API + price trend + sell advice |
| WhatsApp Alerts | whatsapp_alerts.py | Meta Cloud API subscription + messaging |
| Email Alerts | email_alerts.py | SMTP-based irrigation report emailing |
| Fertilizer Module | fertilizer_recommendation.py | Random Forest fertilizer recommendation |
| Solar Estimator | solar_estimator.py | Solar income vs farming income calculator |
| Main Application | app.py | Flask routing + integration of all modules |

---

## 3.8   Selection of Technology and Justification

| Technology | Justification |
|---|---|
| **Python** | Industry-standard for ML/AI; extensive library ecosystem (scikit-learn, TensorFlow, NumPy, Pandas) |
| **Flask** | Lightweight, easy to set up, no ORM overhead, perfect for single-developer projects |
| **Random Forest** | High accuracy for tabular data, resistant to overfitting, interpretable feature importance |
| **MobileNetV2** | Pre-trained on ImageNet, transfer learning reduces training data requirements, efficient for image classification |
| **JSON Storage** | Eliminates database server dependency, easy to read/write, sufficient for small-scale deployment |
| **Bootstrap 5** | Responsive design, mobile-first, rich component library, no jQuery dependency |
| **OpenWeatherMap API** | Free tier available, reliable, covers all Gujarat cities, returns detailed weather + forecast data |
| **Agmarknet API** | Official Government of India agricultural market data source |

---

## 3.9   Summary

This chapter analyzed the current agricultural information system, identified its weaknesses, defined functional and non-functional requirements for the proposed system, assessed feasibility, and described the proposed system's workflow, features, modules, and technology choices. The analysis confirms the need for and feasibility of the Smart Agricultural System.

---
