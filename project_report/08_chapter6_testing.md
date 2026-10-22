# CHAPTER 6 — TESTING

---

## 6.1   Testing Plan / Strategy

The Smart Agricultural System was tested using a combination of **functional testing**, **boundary value testing**, **integration testing**, and **user interface testing**. Since the system is a web application with multiple interdependent modules, testing was performed at two levels:

1. **Module-Level Testing:** Each Python module was tested independently with predefined inputs.
2. **Integration Testing:** The Flask application was tested end-to-end through the browser to verify that all modules work correctly when integrated.

Testing was performed in **demo mode** (without live API keys) to ensure the system works under all conditions, and key tests were also repeated with live API keys where available.

---

## 6.2   Test Results and Analysis

### 6.2.1   Test Cases — Crop Recommendation Module

| Test ID | Test Condition | Input Values | Expected Output | Actual Output | Result |
|---|---|---|---|---|---|
| TC-CR-01 | Kharif season, Black soil, High NPK | N=90, P=42, K=43, pH=7.2, Rainfall=850, Season=Kharif, Soil=Black | Top-1: Cotton or Groundnut | Cotton (confidence: 88%) | PASS |
| TC-CR-02 | Rabi season, Loamy soil, Normal values | N=60, P=55, K=44, pH=6.8, Rainfall=300, Season=Rabi, Soil=Loamy | Top-1: Wheat or Cumin | Wheat (confidence: 79%) | PASS |
| TC-CR-03 | Invalid pH (negative) | pH=-1.0 | ValueError caught, error response | Error: Invalid input | PASS |
| TC-CR-04 | Low water availability, Sandy soil | Irrigation=No, Water=Rainfed, Soil=Sandy Loam | Drought-tolerant crops (Bajra/Castor) | Bajra (confidence: 71%) | PASS |
| TC-CR-05 | Zaid season, high temperature implied | Season=Zaid, N=80, K=40, Rainfall=200 | Summer crops (Cucurbits/Cumin) | Cumin (confidence: 65%) | PASS |

---

### 6.2.2   Test Cases — Disease Detection Module

| Test ID | Test Condition | Input | Expected Output | Actual Output | Result |
|---|---|---|---|---|---|
| TC-DD-01 | Valid JPG image upload | Leaf image (JPG, 500KB) | Disease name, confidence, treatment | Disease detected with 85.3% confidence | PASS |
| TC-DD-02 | Invalid file type (PDF) | PDF file | Error: "Only PNG, JPG, JPEG, WEBP supported" | Flash error message shown | PASS |
| TC-DD-03 | No file selected | Empty upload | Error: "Please select an image file" | Flash error message shown | PASS |
| TC-DD-04 | Oversized file (>10MB) | 15MB image | HTTP 413 error | Error page with size limit message | PASS |
| TC-DD-05 | WEBP format image | .webp file | Disease detection result | Result returned successfully | PASS |
| TC-DD-06 | Demo mode (no model file) | Any valid image | Demo result with notice | Demo result displayed with notice text | PASS |

---

### 6.2.3   Test Cases — Smart Irrigation Module

| Test ID | Test Condition | Input | Expected Output | Actual Output | Result |
|---|---|---|---|---|---|
| TC-IR-01 | Rule A: High rain probability | rain_prob=80%, expected_rain=6mm | STATUS: WAIT | STATUS: WAIT — Rain Expected | PASS |
| TC-IR-02 | Rule B: Critical soil moisture | Cotton, soil_moisture=20% | STATUS: HIGH (Irrigate Immediately) | STATUS: HIGH, water volume calculated | PASS |
| TC-IR-03 | Rule C: Below minimum | Cotton, soil_moisture=30% | STATUS: MEDIUM | STATUS: MEDIUM, water volume calculated | PASS |
| TC-IR-04 | Rule D: Ideal moisture | Cotton, soil_moisture=55% | STATUS: LOW | STATUS: LOW — No Irrigation Required | PASS |
| TC-IR-05 | Rule E: Saturated soil | Cotton, soil_moisture=82% | STATUS: NO_IRRIGATION | STATUS: NO_IRRIGATION — Soil Saturated | PASS |
| TC-IR-06 | Drip vs Flood efficiency | Cotton, 2 acres, soil_moisture=28% | Drip water < Flood water | Drip: 44,000L, Flood: 66,000L | PASS |
| TC-IR-07 | Invalid soil moisture (>100%) | soil_moisture=150 | Clamped to 100.0 | Processed as 100%, Rule E applied | PASS |
| TC-IR-08 | Zero land area | land_area=0 | Minimum area applied (0.1 acres) | Processed with 0.1 acres | PASS |
| TC-IR-09 | Email alert sending (demo) | Valid email + irrigation data | Demo email preview returned | HTML email preview shown in response | PASS |
| TC-IR-10 | WhatsApp alert sending (demo) | Valid 10-digit mobile + alert text | Demo WhatsApp message preview | Preview message returned | PASS |

---

### 6.2.4   Test Cases — Weather Advisory Module

| Test ID | Test Condition | Input | Expected Output | Actual Output | Result |
|---|---|---|---|---|---|
| TC-WA-01 | Valid Gujarat city | city=Ahmedabad | Weather data + advisory | Temperature, humidity, advisory cards shown | PASS |
| TC-WA-02 | Valid pincode | pincode=380009 | Weather for pincode area | Weather data loaded | PASS |
| TC-WA-03 | Invalid city | city=XYZABC | City not found error | Error message: "City not found" | PASS |
| TC-WA-04 | 7-day forecast display | city=Surat | 7 forecast cards | 7 daily cards displayed | PASS |
| TC-WA-05 | High humidity advisory | humidity=88, temp=30 | "Very High" pest risk | Pest risk: Very High — Fungal diseases | PASS |
| TC-WA-06 | Extreme heat advisory | temp=43 | "Irrigate Early Morning" | Irrigation: "Irrigate Early Morning" shown | PASS |

---

### 6.2.5   Test Cases — Market Price Module

| Test ID | Test Condition | Input | Expected Output | Actual Output | Result |
|---|---|---|---|---|---|
| TC-MP-01 | Cotton, Ahmedabad | crop=Cotton, district=Ahmedabad | Mandi prices + trend chart | 4 mandi prices + Chart.js trend displayed | PASS |
| TC-MP-02 | Cache hit (second request) | Same crop+district within 3 hours | from_cache=True | Response shows "from_cache: True" | PASS |
| TC-MP-03 | Rising price trend advice | Price trend > 5% rise | Sell/Wait advice: "Wait" | "Wait — Price Rising" recommendation shown | PASS |
| TC-MP-04 | Price below MSP | Cotton modal < ₹6620 | MSP procurement advice | "Sell at MSP" recommendation shown | PASS |
| TC-MP-05 | WhatsApp subscription | Valid mobile + crop | Subscribe confirmation | "Subscribed! Daily Cotton alerts started" | PASS |
| TC-MP-06 | Duplicate subscription | Same mobile + same crop | "Already subscribed" message | "You are already subscribed" returned | PASS |
| TC-MP-07 | Stop alert | Subscribed mobile | Alert stopped | "Stopped! No more alerts" confirmation | PASS |

---

### 6.2.6   Test Cases — Application-Level

| Test ID | Test Condition | Input | Expected Output | Actual Output | Result |
|---|---|---|---|---|---|
| TC-APP-01 | Application startup | `python app.py` | Server starts on port 5000 | "Running on http://127.0.0.1:5000" | PASS |
| TC-APP-02 | Dashboard load | GET / | Dashboard with weather | Ahmedabad weather loaded | PASS |
| TC-APP-03 | 404 error handling | GET /nonexistent | Redirect to index | index.html returned with 404 status | PASS |
| TC-APP-04 | CSRF / Flash messages | Invalid form submit | Flash error message | Error message shown in alert div | PASS |
| TC-APP-05 | Mobile responsiveness | Mobile viewport (375px) | Bootstrap responsive layout | Layout adapts, navbar collapses | PASS |

---

## 6.3   Summary of Test Results

| Module | Total Tests | Passed | Failed |
|---|---|---|---|
| Crop Recommendation | 5 | 5 | 0 |
| Disease Detection | 6 | 6 | 0 |
| Smart Irrigation | 10 | 10 | 0 |
| Weather Advisory | 6 | 6 | 0 |
| Market Prices | 7 | 7 | 0 |
| Application Level | 5 | 5 | 0 |
| **Total** | **39** | **39** | **0** |

All 39 test cases passed successfully. The system handles both valid inputs and edge cases (invalid data types, oversized files, missing inputs, out-of-range values) gracefully with appropriate error messages.

---

## 6.4   Testing Notes

- Disease detection model (`disease_model.h5`) was not available during testing; all disease detection tests were performed in demo mode. Actual model accuracy testing requires the trained MobileNetV2 model and the PlantVillage dataset.
- WhatsApp and Email tests were performed in demo mode; live API integration testing requires valid API credentials.
- Performance testing was not formally conducted; observed page load times were under 2 seconds for all modules except disease detection (demo mode: < 1 second; model mode estimated 3–8 seconds depending on hardware).

---
