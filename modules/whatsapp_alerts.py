"""
WhatsApp Crop Price Alert Module
Handles: subscribe, change crop, stop alert, send message via Meta WhatsApp Cloud API.
Storage: data/whatsapp_alerts.json (no database needed)
"""

import os
import re
import json
import requests
from datetime import datetime

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_JSON = os.path.join(BASE_DIR, "config.json")
ALERTS_JSON = os.path.join(BASE_DIR, "data", "whatsapp_alerts.json")

# Gujarat crops supported for alerts
ALERT_CROPS = [
    ("Cotton",    "Cotton"),
    ("Groundnut", "Groundnut"),
    ("Castor",    "Castor"),
    ("Cumin",     "Cumin"),
    ("Wheat",     "Wheat"),
    ("Rice",      "Rice"),
    ("Bajra",     "Bajra"),
    ("Maize",     "Maize"),
    ("Sugarcane", "Sugarcane"),
    ("Onion",     "Onion"),
    ("Tomato",    "Tomato"),
    ("Mango",     "Mango"),
]


# ── Helpers ────────────────────────────────────────────────────

def _load_config() -> dict:
    with open(CONFIG_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_db() -> dict:
    with open(ALERTS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: dict):
    with open(ALERTS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _normalize_number(raw: str) -> str:
    """Normalize to E.164 format: +91XXXXXXXXXX"""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return "+91" + digits
    if len(digits) == 12 and digits.startswith("91"):
        return "+" + digits
    if len(digits) == 13 and digits.startswith("091"):
        return "+" + digits[1:]
    return "+" + digits


def _validate_number(number: str) -> tuple[bool, str]:
    """Returns (is_valid, normalized_number_or_error)"""
    try:
        norm = _normalize_number(number)
        digits = norm.replace("+", "")
        if len(digits) != 12 or not digits.startswith("91"):
            return False, "Invalid Indian mobile number. Please enter a 10-digit Gujarat number."
        return True, norm
    except Exception:
        return False, "Invalid number format."


def _find_subscriber(number: str, db: dict) -> dict | None:
    for sub in db["subscribers"]:
        if sub["whatsapp_number"] == number:
            return sub
    return None


# ── Core Operations ────────────────────────────────────────────

def subscribe(raw_number: str, crop: str) -> dict:
    """Subscribe a farmer to daily price alerts for a specific crop."""
    valid, result = _validate_number(raw_number)
    if not valid:
        return {"success": False, "error": result}

    number = result
    crop_names = [c for c, _ in ALERT_CROPS]
    if crop not in crop_names:
        return {"success": False, "error": f"Crop '{crop}' not supported for alerts."}

    db  = _load_db()
    now = datetime.now().isoformat()

    existing = _find_subscriber(number, db)
    crop_gu  = dict(ALERT_CROPS).get(crop, crop)

    if existing:
        old_crop = existing["crop"]
        old_crop_gu = dict(ALERT_CROPS).get(old_crop, old_crop)

        if existing["status"] == "active" and existing["crop"] == crop:
            return {
                "success": True,
                "action":  "already_subscribed",
                "message": f"You are already subscribed for {crop} price alerts.",
                "number":  number,
                "crop":    crop,
                "crop_gu": crop_gu,
            }

        # Update existing subscriber
        existing["crop"]       = crop
        existing["crop_gu"]    = crop_gu
        existing["status"]     = "active"
        existing["updated_at"] = now
        _save_db(db)

        return {
            "success":  True,
            "action":   "updated",
            "message":  f"Alert updated! You will now receive daily {crop} price alerts.",
            "number":   number,
            "crop":     crop,
            "crop_gu":  crop_gu,
            "old_crop": old_crop,
            "old_crop_gu": old_crop_gu,
        }

    # New subscriber
    db["subscribers"].append({
        "id":               len(db["subscribers"]) + 1,
        "whatsapp_number":  number,
        "crop":             crop,
        "crop_gu":          crop_gu,
        "status":           "active",
        "created_at":       now,
        "updated_at":       now,
        "last_sent_at":     None,
        "total_sent":       0,
    })
    _save_db(db)

    # Send instant welcome message
    welcome_result = send_welcome_message(number, crop, crop_gu)

    return {
        "success":       True,
        "action":        "subscribed",
        "message":       f"Subscribed! You will receive daily {crop} price alerts on WhatsApp.",
        "number":        number,
        "crop":          crop,
        "crop_gu":       crop_gu,
        "welcome_sent":  welcome_result.get("success", False),
        "welcome_demo":  welcome_result.get("demo", True),
        "welcome_preview": welcome_result.get("preview", ""),
    }


def stop_alert(raw_number: str) -> dict:
    """Unsubscribe a farmer from all alerts."""
    valid, result = _validate_number(raw_number)
    if not valid:
        return {"success": False, "error": result}

    number = result
    db     = _load_db()
    sub    = _find_subscriber(number, db)

    if not sub:
        return {
            "success": False,
            "error":   "This number is not subscribed to any alerts.",
        }

    if sub["status"] == "stopped":
        return {
            "success": True,
            "action":  "already_stopped",
            "message": "Your alerts were already stopped.",
            "number":  number,
        }

    sub["status"]     = "stopped"
    sub["updated_at"] = datetime.now().isoformat()
    _save_db(db)

    return {
        "success":  True,
        "action":   "stopped",
        "message":  f"Stopped! No more {sub['crop']} price alerts will be sent to {number}.",
        "number":   number,
        "crop":     sub["crop"],
    }


def get_subscribers_for_crop(crop: str) -> list:
    """Return all active subscribers for a given crop."""
    db = _load_db()
    return [
        s for s in db["subscribers"]
        if s["crop"] == crop and s["status"] == "active"
    ]


def get_all_active_subscribers() -> list:
    """Return all active subscribers."""
    db = _load_db()
    return [s for s in db["subscribers"] if s["status"] == "active"]


def get_all_subscribers() -> list:
    """Return all subscribers (for admin view)."""
    db = _load_db()
    return db["subscribers"]


def get_stats() -> dict:
    """Return alert statistics."""
    db    = _load_db()
    subs  = db["subscribers"]
    active  = [s for s in subs if s["status"] == "active"]
    stopped = [s for s in subs if s["status"] == "stopped"]

    crop_counts = {}
    for s in active:
        crop_counts[s["crop"]] = crop_counts.get(s["crop"], 0) + 1

    return {
        "total":        len(subs),
        "active":       len(active),
        "stopped":      len(stopped),
        "total_sent":   db.get("total_sent", 0),
        "last_run":     db.get("last_daily_run"),
        "crop_counts":  crop_counts,
    }


# ── Welcome Message ───────────────────────────────────────────

def send_welcome_message(number: str, crop: str, crop_gu: str) -> dict:
    """
    Send an instant welcome message when a farmer subscribes.
    Called immediately after successful subscription.
    """
    message = (
        f"🌾 *Namaste! Smart Agriculture Bot — Gujarat*\n\n"
        f"✅ *Aapna alert sharu thayi gaya!*\n"
        f"_(Your price alerts have started!)_\n\n"
        f"📌 *Selected Crop / Pasand karelan Pak:*\n"
        f"   *{crop}* — *{crop_gu}*\n\n"
        f"⏰ *Daily at 8:00 AM* aapne *{crop_gu}* na\n"
        f"   Gujarat mandi bhaav WhatsApp par malse.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *Useful Commands:*\n"
        f"   • _Subscribe karv market.page_ kholho\n"
        f"   • _Pak badlava:_ Same number par navi crop select karo\n"
        f"   • _Band karv:_ Stop button press karo\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🙏 *Smart Agriculture System — Gujarat*\n"
        f"_Kheti more productive banavo!_"
    )
    return send_whatsapp_message(number, message)


# ── WhatsApp Message Sending ───────────────────────────────────

def _build_message(crop: str, crop_gu: str, prices: list, number: str) -> str:
    """Build the WhatsApp text message body."""
    if not prices:
        return (
            f"🌾 *Smart Agriculture — Gujarat*\n\n"
            f"📢 *{crop} ({crop_gu}) Price Alert*\n\n"
            f"❌ No price data available for today.\n\n"
            f"📅 {datetime.now().strftime('%d %B %Y')}\n\n"
            f"_Reply STOP to unsubscribe._"
        )

    best   = prices[0]
    lines  = [
        f"🌾 *Smart Agriculture — Gujarat*",
        f"",
        f"📢 *Today's {crop} ({crop_gu}) Price*",
        f"",
        f"📍 *Best Market:* {best['market']}",
        f"💰 *Minimum:* ₹{best['min_price']:,}/quintal",
        f"💰 *Maximum:* ₹{best['max_price']:,}/quintal",
        f"📊 *Modal Price:* ₹{best['modal_price']:,}/quintal",
        f"",
    ]

    # Show up to 3 more markets
    if len(prices) > 1:
        lines.append("🏪 *Other Markets:*")
        for p in prices[1:4]:
            lines.append(f"  • {p['market']}: ₹{p['modal_price']:,}/qtl")
        lines.append("")

    lines += [
        f"📅 {datetime.now().strftime('%d %B %Y')}",
        f"",
        f"_Aap {crop_gu} price alert ke liye subscribe kiya hua hai._",
        f"_Reply *STOP* to unsubscribe._",
    ]

    return "\n".join(lines)


def send_whatsapp_message(to_number: str, message_text: str) -> dict:
    """
    Send a WhatsApp text message via Meta Cloud API.
    Falls back to demo mode if API token not configured.
    """
    config     = _load_config()
    api_token  = config.get("whatsapp_api_token", "")
    phone_id   = config.get("whatsapp_phone_number_id", "")
    api_ver    = config.get("whatsapp_api_version", "v19.0")
    demo_mode  = config.get("whatsapp_demo_mode", True) or \
                 not api_token or api_token == "YOUR_META_WHATSAPP_API_TOKEN"

    if demo_mode:
        print(f"[DEMO] Would send WhatsApp to {to_number}:\n{message_text}\n")
        return {
            "success":  True,
            "demo":     True,
            "to":       to_number,
            "preview":  message_text[:200] + "..." if len(message_text) > 200 else message_text,
        }

    url     = f"https://graph.facebook.com/{api_ver}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type":  "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to":                to_number.replace("+", ""),
        "type":              "text",
        "text":              {"preview_url": False, "body": message_text},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return {
            "success":    True,
            "demo":       False,
            "to":         to_number,
            "message_id": data.get("messages", [{}])[0].get("id", ""),
        }
    except requests.exceptions.HTTPError as e:
        err = {}
        try:
            err = e.response.json().get("error", {})
        except Exception:
            pass
        return {
            "success": False,
            "error":   err.get("message", str(e)),
            "code":    err.get("code", e.response.status_code),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_price_alert(subscriber: dict, prices: list) -> dict:
    """Build message and send alert to one subscriber. Update DB."""
    crop     = subscriber["crop"]
    crop_gu  = subscriber.get("crop_gu", crop)
    number   = subscriber["whatsapp_number"]

    message  = _build_message(crop, crop_gu, prices, number)
    result   = send_whatsapp_message(number, message)

    if result.get("success"):
        db  = _load_db()
        for s in db["subscribers"]:
            if s["whatsapp_number"] == number:
                s["last_sent_at"]  = datetime.now().isoformat()
                s["total_sent"]    = s.get("total_sent", 0) + 1
                break
        db["total_sent"] = db.get("total_sent", 0) + 1
        _save_db(db)

    return result
