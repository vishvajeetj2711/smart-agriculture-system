# 🌾 Smart Agricultural System for Gujarat Farmers

An AI-powered, web-based decision support platform for Gujarat farmers built with Python & Flask.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Features

| Module | Description |
|---|---|
| 🌱 **Crop Recommendation** | Random Forest + Rule-based engine (15 soil & water parameters) |
| 🍃 **Disease Detection** | MobileNetV2 CNN leaf image analysis (38 disease classes) |
| 💧 **Smart Irrigation** | 5-rule deterministic engine — calculates exact water volume (litres) |
| 🌤️ **Weather Advisory** | Real-time OpenWeatherMap API + bilingual (English + Gujarati) advisories |
| 📈 **Market Prices** | Live Gujarat mandi prices via Agmarknet API + sell/wait recommendation |
| 📱 **WhatsApp Alerts** | Meta Cloud API daily crop price alerts |
| 📧 **Email Alerts** | SMTP irrigation advisory reports |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.12, Flask 3.x
- **ML/AI:** scikit-learn (Random Forest), TensorFlow/Keras (MobileNetV2)
- **Data:** NumPy, Pandas, JSON file storage (no database)
- **Frontend:** HTML5, Bootstrap 5, Chart.js, JavaScript
- **APIs:** OpenWeatherMap, Agmarknet (data.gov.in), Meta WhatsApp Cloud

---

## ⚙️ Setup & Run

### 1. Clone the Repository
```bash
git clone https://github.com/vishvajeet97-tech/Smart-Agriculture-System.git
cd Smart-Agriculture-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
copy config.example.json config.json
```
Then edit `config.json` and add your API keys:
- `openweathermap_api_key` → Get from [openweathermap.org](https://openweathermap.org/api)
- `agmarknet_api_key` → Get from [data.gov.in](https://data.gov.in)
- `whatsapp_api_token` → Get from [Meta Developers](https://developers.facebook.com/docs/whatsapp/cloud-api)
- `smtp_username` / `smtp_password` → Gmail App Password

> **Note:** The system works fully in **demo mode** without any API keys!

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
Smart Agricultural System/
├── app.py                        # Main Flask application
├── config.json                   # API keys (not in repo — see config.example.json)
├── config.example.json           # Template for config.json
├── requirements.txt              # Python dependencies
├── modules/                      # Feature modules
│   ├── crop_recommendation.py
│   ├── disease_detection.py
│   ├── weather_advisory.py
│   ├── smart_irrigation.py
│   ├── market_prices.py
│   ├── whatsapp_alerts.py
│   ├── email_alerts.py
│   ├── fertilizer_recommendation.py
│   └── solar_estimator.py
├── models/                       # ML model files (train separately)
│   └── train_models.py
├── data/                         # JSON data files
├── templates/                    # HTML templates (Bootstrap 5)
├── static/                       # CSS, JS, images
└── project_report/               # B.Tech project report (PDF + MD files)
```

---

## 🤖 ML Models

| Model | Algorithm | Purpose |
|---|---|---|
| `crop_model.pkl` | Random Forest | Crop recommendation |
| `fertilizer_model.pkl` | Random Forest | Fertilizer recommendation |
| `disease_model.h5` | MobileNetV2 CNN | Plant disease detection |

> Models are not included in the repo due to file size. Train them using `models/train_models.py`.
> Without models, the system runs in **demo mode** automatically.

---

## 📄 Project Report

The complete B.Tech project report is available in the `project_report/` folder:
- 📄 `Smart_Agricultural_System_BTech_Report.pdf` — Full formatted PDF report
- Individual chapter markdown files (Chapter 1–7)

---

## 👨‍💻 Developer

**Jadav Vishvajeet**
B.Tech Computer Engineering
College of Technology, Silver Oak University, Ahmedabad
Academic Year: 2026–2027

---

## 📜 License

This project is licensed under the MIT License.
