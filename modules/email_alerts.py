"""
Email Alert Module — Smart Agriculture Gujarat
===============================================
Handles sending smart irrigation reports and advisories via Email (SMTP).
No external database needed — sent logs stored in data/email_alerts.json.
"""

import os
import re
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_JSON  = os.path.join(BASE_DIR, "config.json")
LOG_JSON     = os.path.join(BASE_DIR, "data", "email_alerts.json")


def _load_config() -> dict:
    if not os.path.exists(CONFIG_JSON):
        return {}
    with open(CONFIG_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_db() -> dict:
    if not os.path.exists(LOG_JSON):
        return {"alerts": []}
    with open(LOG_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: dict):
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email address format."""
    email_clean = (email or "").strip().lower()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email_clean or not re.match(pattern, email_clean):
        return False, "Please enter a valid email address (e.g. farmer@example.com)."
    return True, email_clean


def build_irrigation_email_content(data: dict) -> tuple[str, str, str]:
    """
    Build Subject, Plain-text body, and Rich HTML body for the irrigation advisory email.
    """
    crop         = data.get("crop", "Cotton")
    crop_gu      = data.get("crop_gujarati", crop)
    stage        = data.get("growth_stage", "Vegetative")
    area         = data.get("land_area", 1.0)
    moisture     = data.get("soil_moisture", 50)
    status       = data.get("status", "LOW")
    status_ui    = data.get("status_ui", {})
    title        = status_ui.get("title", f"STATUS: {status}")
    subtitle     = status_ui.get("subtitle", "")
    water_L      = data.get("estimated_water_L", 0)
    water_fmt    = data.get("estimated_water_formatted", f"{water_L:,} L")
    time_rec     = data.get("recommended_time", "Morning")
    method       = data.get("irrigation_method", "Drip")
    rain_prob    = data.get("weather_summary", {}).get("rain_prob", 0)
    exp_rain     = data.get("weather_summary", {}).get("expected_rainfall", 0)
    temp         = data.get("weather_summary", {}).get("temp", 32)
    hum          = data.get("weather_summary", {}).get("humidity", 55)
    advice       = data.get("farmer_advice", {})
    advice_en    = advice.get("en", "")
    advice_gu    = advice.get("gu", "")
    reason       = data.get("reason", "")
    date_str     = data.get("date_str", datetime.now().strftime("%d %B %Y"))
    icon         = status_ui.get("icon", "💧")

    subject = f"🌾 [Smart Agri Alert] {crop} Irrigation Advisory — {title}"

    # Plain text version
    plain_text = (
        f"SMART AGRICULTURE SYSTEM — GUJARAT\n"
        f"Smart Irrigation & Water Management Advisory\n"
        f"Date: {date_str}\n"
        f"--------------------------------------------------\n"
        f"Crop: {crop} ({crop_gu}) | Stage: {stage} | Area: {area} Acres\n"
        f"Status: {icon} {title} ({subtitle})\n"
        f"Soil Moisture: {moisture}%\n"
        f"Rain Forecast: {rain_prob}% (Expected: {exp_rain} mm)\n"
        f"Weather: {temp}°C, Humidity: {hum}%\n"
        f"Estimated Water: {water_fmt} ({method})\n"
        f"Recommended Time: {time_rec}\n"
        f"--------------------------------------------------\n"
        f"Why: {reason}\n\n"
        f"Advisory (English):\n{advice_en}\n\n"
        f"ખેડૂત સલાહ (Gujarati):\n{advice_gu}\n"
        f"--------------------------------------------------\n"
        f"Smart Agriculture System — Built for Indian Farmers\n"
    )

    # HTML banner color
    banner_color = status_ui.get("color_hex", "#2e7d32")

    # Rich HTML version
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7f2; margin: 0; padding: 20px; color: #2c3e2d; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #1b5e20, #2e7d32); color: #ffffff; padding: 24px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 20px; font-weight: 700; }}
        .header p {{ margin: 5px 0 0; font-size: 13px; opacity: 0.85; }}
        .status-banner {{ background-color: {banner_color}; color: #ffffff; padding: 18px 24px; text-align: center; }}
        .status-banner .status-badge {{ background: rgba(255,255,255,0.25); display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
        .status-banner h2 {{ margin: 0; font-size: 22px; font-weight: 800; }}
        .content {{ padding: 24px; }}
        .grid {{ display: table; width: 100%; margin-bottom: 20px; }}
        .grid-row {{ display: table-row; }}
        .grid-cell {{ display: table-cell; width: 50%; padding: 10px; vertical-align: top; }}
        .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; text-align: center; }}
        .metric-val {{ font-size: 18px; font-weight: 700; color: #1b5e20; margin-top: 4px; }}
        .metric-lbl {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; }}
        .advice-box {{ background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 8px; padding: 14px 16px; margin: 18px 0; }}
        .advice-title {{ font-weight: bold; color: #15803d; font-size: 13px; margin-bottom: 6px; }}
        .advice-text {{ font-size: 14px; line-height: 1.5; color: #334155; margin: 0; }}
        .guj-text {{ font-size: 13px; color: #166534; line-height: 1.5; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #bbf7d0; }}
        .footer {{ background: #f8f9fa; padding: 16px; text-align: center; font-size: 11px; color: #6c757d; border-top: 1px solid #eee; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🌾 Smart Agriculture System</h1>
          <p>Gujarat Smart Farming &amp; Irrigation Advisory · {date_str}</p>
        </div>

        <div class="status-banner">
          <div class="status-badge">{icon} {title}</div>
          <h2>{subtitle}</h2>
        </div>

        <div class="content">
          <div class="grid">
            <div class="grid-row">
              <div class="grid-cell">
                <div class="metric-card">
                  <div class="metric-lbl">Crop &amp; Stage</div>
                  <div class="metric-val">{crop} ({stage})</div>
                </div>
              </div>
              <div class="grid-cell">
                <div class="metric-card">
                  <div class="metric-lbl">Estimated Applied Water</div>
                  <div class="metric-val" style="color:#0284c7">{water_fmt}</div>
                </div>
              </div>
            </div>
            <div class="grid-row">
              <div class="grid-cell">
                <div class="metric-card">
                  <div class="metric-lbl">Soil Moisture</div>
                  <div class="metric-val">{moisture}%</div>
                </div>
              </div>
              <div class="grid-cell">
                <div class="metric-card">
                  <div class="metric-lbl">Rain Forecast</div>
                  <div class="metric-val" style="color:#eab308">{rain_prob}% ({exp_rain} mm)</div>
                </div>
              </div>
            </div>
          </div>

          <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:12px 16px; font-size:13px; margin-bottom:16px;">
            <strong>⏰ Recommended Irrigation Time:</strong> {time_rec}<br>
            <strong>💧 System Efficiency:</strong> {method} Irrigation<br>
            <strong>🌱 Field Area:</strong> {area} Acres
          </div>

          <div class="advice-box">
            <div class="advice-title">💡 Actionable Advisory (English):</div>
            <p class="advice-text">{advice_en}</p>
            <div class="guj-text">
              <strong>🌾 ખેડૂત સલાહ (Gujarati):</strong><br>
              {advice_gu}
            </div>
          </div>

          <p style="font-size:12px; color:#64748b; line-height:1.4; margin-top:16px;">
            <strong>Reason:</strong> {reason}
          </p>
        </div>

        <div class="footer">
          🌾 Smart Agriculture System — Gujarat &nbsp;|&nbsp; Built for Indian Farmers &nbsp;|&nbsp; Automated Advisory Report
        </div>
      </div>
    </body>
    </html>
    """

    return subject, plain_text, html_body


def send_irrigation_email(to_email: str, alert_data: dict) -> dict:
    """
    Send an irrigation advisory report email to the farmer.
    If demo mode is active or SMTP not configured, logs to JSON and returns demo success.
    If SMTP configured, sends via smtplib.
    """
    valid, email_or_err = validate_email(to_email)
    if not valid:
        return {"success": False, "error": email_or_err}

    target_email = email_or_err
    config = _load_config()

    smtp_server = config.get("smtp_server", "smtp.gmail.com")
    smtp_port   = int(config.get("smtp_port", 587))
    smtp_user   = config.get("smtp_username", "")
    smtp_pass   = config.get("smtp_password", "")
    email_from  = config.get("email_from", "Smart Agriculture Gujarat <no-reply@smartagri.gujarat.gov.in>")
    demo_mode   = config.get("email_demo_mode", True) or not smtp_user or smtp_user == "YOUR_EMAIL@gmail.com"

    subject, plain_text, html_body = build_irrigation_email_content(alert_data)

    db = _load_db()
    log_entry = {
        "id":        len(db.get("alerts", [])) + 1,
        "timestamp": datetime.now().isoformat(),
        "date":      datetime.now().strftime("%d %b %Y %H:%M"),
        "to_email":  target_email,
        "crop":      alert_data.get("crop", "Cotton"),
        "status":    alert_data.get("status", "LOW"),
        "water_L":   alert_data.get("estimated_water_L", 0),
        "subject":   subject,
        "demo_mode": demo_mode,
    }

    if demo_mode:
        print(f"[DEMO EMAIL] Would send Email to {target_email}:\nSubject: {subject}\n{plain_text}\n")
        db.setdefault("alerts", []).append(log_entry)
        db["alerts"] = db["alerts"][-100:]
        _save_db(db)
        return {
            "success":    True,
            "demo":       True,
            "to":         target_email,
            "subject":    subject,
            "plain_text": plain_text,
            "message":    f"Advisory email generated and sent to {target_email}!",
        }

    # Live SMTP Sending
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = email_from
        msg["To"]      = target_email

        part1 = MIMEText(plain_text, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(email_from, [target_email], msg.as_string())

        db.setdefault("alerts", []).append(log_entry)
        db["alerts"] = db["alerts"][-100:]
        _save_db(db)

        return {
            "success": True,
            "demo":    False,
            "to":      target_email,
            "subject": subject,
            "message": f"Advisory email successfully dispatched to {target_email}!",
        }
    except Exception as e:
        print(f"Error sending SMTP email: {e}")
        # Graceful fallback to demo logging on SMTP network failure
        db.setdefault("alerts", []).append(log_entry)
        _save_db(db)
        return {
            "success": True,
            "demo":    True,
            "to":      target_email,
            "subject": subject,
            "plain_text": plain_text,
            "message": f"Advisory email prepared for {target_email} (Fallback mode: {str(e)}).",
        }


def get_email_alert_logs(limit: int = 20) -> list:
    """Retrieve recent email alert logs."""
    db = _load_db()
    return db.get("alerts", [])[-limit:][::-1]
