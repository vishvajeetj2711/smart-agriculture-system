"""
Agricultural Market Price Tracker — Gujarat Edition
Fetches mandi prices from data.gov.in Agmarknet API for Gujarat mandis.
Bilingual: English + Gujarati
"""

import os
import json
import requests
from datetime import datetime, timedelta
import random

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_JSON  = os.path.join(BASE_DIR, "config.json")
CACHE_JSON   = os.path.join(BASE_DIR, "data", "market_cache.json")
HISTORY_JSON = os.path.join(BASE_DIR, "data", "price_history.json")
USER_HIST    = os.path.join(BASE_DIR, "data", "user_history.json")

CACHE_TTL_HOURS = 3

# ── Gujarat Mandis by District ─────────────────────────────────
GUJARAT_MANDIS = {
    "Ahmedabad":   ["Ahmedabad", "Bavla", "Dholka", "Sanand"],
    "Anand":       ["Anand", "Khambhat", "Petlad", "Sojitra"],
    "Banaskantha": ["Palanpur", "Deesa", "Dhanera", "Tharad"],
    "Bharuch":     ["Bharuch", "Ankleshwar", "Jambusar"],
    "Bhavnagar":   ["Bhavnagar", "Mahuva", "Palitana", "Talaja"],
    "Gandhinagar": ["Gandhinagar", "Kalol", "Mansa"],
    "Jamnagar":    ["Jamnagar", "Dhrol", "Kalavad"],
    "Junagadh":    ["Junagadh", "Keshod", "Veraval", "Mangrol"],
    "Kheda":       ["Nadiad", "Kapadvanj", "Mehmedabad"],
    "Kutch":       ["Bhuj", "Gandhidham", "Mundra", "Nakhatrana"],
    "Mehsana":     ["Mehsana", "Unjha", "Visnagar", "Kadi"],
    "Rajkot":      ["Rajkot", "Gondal", "Jetpur", "Morbi"],
    "Surat":       ["Surat", "Bardoli", "Mandvi", "Olpad"],
    "Surendranagar":["Surendranagar","Wadhwan","Dhangadhra","Halvad"],
    "Vadodara":    ["Vadodara", "Karjan", "Padra", "Dabhoi"],
}

# Flatten list of all Gujarat mandis
ALL_GUJARAT_MANDIS = [m for ms in GUJARAT_MANDIS.values() for m in ms]

# ── Gujarat crops with Gujarati names & MSP ────────────────────
GUJARAT_CROPS = {
    "Cotton":     {"base": 6620, "msp": 6620, "gujarati": "",    "unit": "per quintal"},
    "Groundnut":  {"base": 6377, "msp": 6377, "gujarati": "",   "unit": "per quintal"},
    "Castor":     {"base": 6200, "msp": 0,    "gujarati": "",   "unit": "per quintal"},
    "Cumin":      {"base": 25000,"msp": 0,    "gujarati": "",    "unit": "per quintal"},
    "Wheat":      {"base": 2275, "msp": 2275, "gujarati": "",     "unit": "per quintal"},
    "Rice":       {"base": 2183, "msp": 2183, "gujarati": "",   "unit": "per quintal"},
    "Bajra":      {"base": 2500, "msp": 2500, "gujarati": "",   "unit": "per quintal"},
    "Maize":      {"base": 1870, "msp": 1870, "gujarati": "",    "unit": "per quintal"},
    "Sugarcane":  {"base": 340,  "msp": 340,  "gujarati": "",   "unit": "per quintal"},
    "Onion":      {"base": 1800, "msp": 0,    "gujarati": "",  "unit": "per quintal"},
    "Tomato":     {"base": 1500, "msp": 0,    "gujarati": "",  "unit": "per quintal"},
    "Mango":      {"base": 3500, "msp": 0,    "gujarati": "",    "unit": "per quintal"},
}


def _load_config():
    with open(CONFIG_JSON, "r") as f:
        return json.load(f)


def _load_cache():
    with open(CACHE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_cache(data: dict):
    with open(CACHE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_price_history():
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_price_history(data: dict):
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _save_user_history(entry: dict):
    with open(USER_HIST, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["market_queries"].append(entry)
    history["market_queries"] = history["market_queries"][-50:]
    with open(USER_HIST, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _generate_demo_prices(crop: str, district: str) -> list:
    """Generate realistic demo mandi prices for Gujarat district."""
    crop_info  = GUJARAT_CROPS.get(crop, {"base": 2000, "msp": 0, "gujarati": crop, "unit": "per quintal"})
    base_price = crop_info["base"]
    mandis     = GUJARAT_MANDIS.get(district, ALL_GUJARAT_MANDIS[:5])

    random.seed(hash(crop + district + datetime.now().strftime("%Y%m%d")))
    results = []
    for mandi in mandis:
        variation   = random.uniform(-0.10, 0.15)
        min_price   = round(base_price * (1 + variation - 0.04))
        max_price   = round(base_price * (1 + variation + 0.06))
        modal_price = round(base_price * (1 + variation))
        results.append({
            "market":       mandi,
            "district":     district,
            "state":        "Gujarat",
            "commodity":    crop,
            "gujarati_commodity": crop_info["gujarati"],
            "variety":      "General",
            "min_price":    min_price,
            "max_price":    max_price,
            "modal_price":  modal_price,
            "date":         datetime.now().strftime("%d/%m/%Y"),
        })

    results.sort(key=lambda x: x["modal_price"], reverse=True)
    return results


def _generate_price_trend(crop: str, current_price: int) -> dict:
    """7-day price trend with Gujarati labels."""
    random.seed(hash(crop + datetime.now().strftime("%Y%m%d")))
    labels_en = []
    labels_gu = []
    prices    = []
    price     = current_price

    gu_days = ["", "", "", "", "", "", ""]

    for i in range(6, -1, -1):
        date   = datetime.now() - timedelta(days=i)
        labels_en.append(date.strftime("%d %b"))
        labels_gu.append(gu_days[date.weekday()])
        change = random.uniform(-0.03, 0.04)
        price  = max(500, round(price * (1 + change)))
        prices.append(price)

    trend_pct = round((prices[-1] - prices[0]) / prices[0] * 100, 1)
    if trend_pct > 3:
        trend = {"direction": "Rising",  "gujarati": "   ", "color": "success", "icon": "📈", "pct": trend_pct}
    elif trend_pct < -3:
        trend = {"direction": "Falling", "gujarati": "   ", "color": "danger",  "icon": "📉", "pct": abs(trend_pct)}
    else:
        trend = {"direction": "Stable",  "gujarati": "  ",     "color": "warning", "icon": "➡️", "pct": abs(trend_pct)}

    return {"labels": labels_en, "labels_gu": labels_gu, "prices": prices, "trend": trend}


def _generate_sell_advice(crop: str, prices: list, trend: dict, msp: int) -> dict:
    """AI-based sell/wait advice — bilingual."""
    if not prices:
        return {"advice": "Insufficient data", "gujarati_advice": "  ",
                "color": "secondary", "icon": "❓"}

    best_price  = max(p["modal_price"] for p in prices)
    best_market = next(p for p in prices if p["modal_price"] == best_price)
    avg_price   = sum(p["modal_price"] for p in prices) / len(prices)
    trend_dir   = trend["trend"]["direction"]
    trend_pct   = trend["trend"]["pct"]

    if best_price < msp * 1.02 and msp > 0:
        return {
            "recommendation":    "Sell at MSP /   ",
            "gujarati_advice":   f"  (₹{best_price}) MSP (₹{msp})   . "
                                 f"    MSP  .",
            "reason":            f"Current price ₹{best_price} is near MSP ₹{msp}. "
                                 f"Contact government procurement center for MSP sale.",
            "color": "warning", "icon": "⏳",
            "best_market": best_market["market"], "best_price": best_price,
        }
    elif trend_dir == "Rising" and trend_pct > 5:
        return {
            "recommendation":    "Wait — Price Rising /  —  ",
            "gujarati_advice":   f"   {trend_pct}%  . "
                                 f"3-5     —   .",
            "reason":            f"Prices rising {trend_pct}% this week. Wait 3-5 more days.",
            "color": "info", "icon": "📈",
            "best_market": best_market["market"], "best_price": best_price,
        }
    elif trend_dir == "Falling" and trend_pct > 5:
        return {
            "recommendation":    "Sell Now /   ",
            "gujarati_advice":   f" {trend_pct}%   . "
                                 f"  {best_market['market']}    .",
            "reason":            f"Prices falling {trend_pct}%. Sell immediately at {best_market['market']}.",
            "color": "danger", "icon": "🔔",
            "best_market": best_market["market"], "best_price": best_price,
        }
    elif best_price > avg_price * 1.08:
        return {
            "recommendation":    "Sell Now — Good Price /   — ",
            "gujarati_advice":   f"{best_market['market']}  ₹{best_price}    "
                                 f"  (₹{round(avg_price)})  "
                                 f"{round((best_price/avg_price-1)*100)}%  .  .",
            "reason":            f"{best_market['market']} offers ₹{best_price}, "
                                 f"{round((best_price/avg_price-1)*100)}% above state average.",
            "color": "success", "icon": "✅",
            "best_market": best_market["market"], "best_price": best_price,
        }
    else:
        return {
            "recommendation":    "Sell at Best Market /   ",
            "gujarati_advice":   f"  . {best_market['market']}  "
                                 f"₹{best_price}     . "
                                 f"     .",
            "reason":            f"Prices stable. Best at {best_market['market']} (₹{best_price}).",
            "color": "primary", "icon": "🏪",
            "best_market": best_market["market"], "best_price": best_price,
        }


def get_market_prices(crop: str, district: str = "Ahmedabad") -> dict:
    """
    Fetch Gujarat mandi prices for a crop + district.
    Uses live API if key available, else demo mode.
    """
    config  = _load_config()
    api_key = config.get("agmarknet_api_key", "")
    demo    = (not api_key or api_key == "YOUR_DATA_GOV_IN_API_KEY")

    cache     = _load_cache()
    cache_key = f"{crop}_{district}_gujarat"

    # Check cache freshness
    if cache_key in cache:
        cached      = cache[cache_key]
        cached_time = datetime.fromisoformat(cached["timestamp"])
        if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
            prices     = cached["prices"]
            best_price = max(p["modal_price"] for p in prices) if prices else 2000
            trend      = _generate_price_trend(crop, best_price)
            msp        = GUJARAT_CROPS.get(crop, {}).get("msp", 0)
            advice     = _generate_sell_advice(crop, prices, trend, msp)
            return {"success": True, "prices": prices, "trend": trend,
                    "advice": advice, "from_cache": True,
                    "demo": cached.get("demo", False),
                    "crop_gujarati": GUJARAT_CROPS.get(crop, {}).get("gujarati", crop)}

    if demo:
        prices    = _generate_demo_prices(crop, district)
        demo_flag = True
    else:
        try:
            base_url = config.get("agmarknet_base_url")
            params   = {
                "api-key":            api_key,
                "format":             "json",
                "filters[commodity]": crop,
                "filters[state]":     "Gujarat",
                "filters[district]":  district,
                "limit":              20,
                "offset":             0,
            }
            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()
            data    = resp.json()
            records = data.get("records", [])
            if not records:
                prices    = _generate_demo_prices(crop, district)
                demo_flag = True
            else:
                prices = []
                for r in records:
                    prices.append({
                        "market":       r.get("Market", ""),
                        "district":     r.get("District", district),
                        "state":        "Gujarat",
                        "commodity":    r.get("Commodity", crop),
                        "gujarati_commodity": GUJARAT_CROPS.get(crop, {}).get("gujarati", crop),
                        "variety":      r.get("Variety", "General"),
                        "min_price":    int(r.get("Min Price", 0)),
                        "max_price":    int(r.get("Max Price", 0)),
                        "modal_price":  int(r.get("Modal Price", 0)),
                        "date":         r.get("Arrival Date", ""),
                    })
                prices.sort(key=lambda x: x["modal_price"], reverse=True)
                demo_flag = False
        except Exception:
            prices    = _generate_demo_prices(crop, district)
            demo_flag = True

    cache[cache_key] = {
        "prices":    prices,
        "timestamp": datetime.now().isoformat(),
        "demo":      demo_flag,
    }
    _save_cache(cache)

    ph = _load_price_history()
    if crop not in ph:
        ph[crop] = []
    if prices:
        best = max(p["modal_price"] for p in prices)
        ph[crop].append({"date": datetime.now().strftime("%d/%m/%Y"), "price": best})
        ph[crop] = ph[crop][-30:]
    _save_price_history(ph)

    best_price = max(p["modal_price"] for p in prices) if prices else 2000
    trend      = _generate_price_trend(crop, best_price)
    msp        = GUJARAT_CROPS.get(crop, {}).get("msp", 0)
    advice     = _generate_sell_advice(crop, prices, trend, msp)

    _save_user_history({"timestamp": datetime.now().isoformat(),
                        "crop": crop, "district": district,
                        "best_price": best_price})

    return {
        "success":        True,
        "prices":         prices,
        "trend":          trend,
        "advice":         advice,
        "msp":            msp,
        "from_cache":     False,
        "demo":           demo_flag,
        "crop_gujarati":  GUJARAT_CROPS.get(crop, {}).get("gujarati", crop),
        "gujarat_crops":  GUJARAT_CROPS,
        "gujarat_mandis": GUJARAT_MANDIS,
    }


def get_gujarat_districts() -> list:
    """Return sorted list of Gujarat districts."""
    return sorted(GUJARAT_MANDIS.keys())


def get_gujarat_crops() -> dict:
    """Return Gujarat crops dict."""
    return GUJARAT_CROPS
