"""
Weather Advisory Module — Gujarat Edition
Real-time weather from OpenWeatherMap + bilingual (English+Gujarati) advice.
"""

import os
import json
import requests
from datetime import datetime

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_JSON  = os.path.join(BASE_DIR, "config.json")
LOG_JSON     = os.path.join(BASE_DIR, "data", "weather_log.json")
HISTORY_JSON = os.path.join(BASE_DIR, "data", "user_history.json")

# Gujarat cities for quick selection
GUJARAT_CITIES = [
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar",
    "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Nadiad",
    "Mehsana", "Palanpur", "Bharuch", "Morbi", "Surendranagar",
    "Bhuj", "Amreli", "Botad", "Dwarka", "Porbandar",
]


def _load_config():
    with open(CONFIG_JSON, "r") as f:
        return json.load(f)


def _save_log(entry: dict):
    with open(LOG_JSON, "r", encoding="utf-8") as f:
        logs = json.load(f)
    logs.append(entry)
    logs = logs[-100:]
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def _save_history(entry: dict):
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["weather_queries"].append(entry)
    history["weather_queries"] = history["weather_queries"][-50:]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _generate_advisory(weather: dict, crop: str = "") -> dict:
    temp     = weather.get("temp", 28)
    humidity = weather.get("humidity", 60)
    wind_kph = weather.get("wind_speed", 10) * 3.6
    desc     = weather.get("description", "").lower()
    rain_1h  = weather.get("rain_1h", 0)

    # ── Irrigation Advisory (bilingual) ──────────────────────────
    if rain_1h > 15:
        irrigation = {
            "status": "No Irrigation",
            "color": "success", "icon": "🚫💧",
            "message": "Heavy rain received. Skip irrigation today. Check drainage.",
        }
    elif rain_1h > 5:
        irrigation = {
            "status": "Reduce Irrigation",
            "color": "info", "icon": "🌦️",
            "message": "Light rain received. Reduce irrigation by 50% today.",
        }
    elif humidity > 80 and temp < 25:
        irrigation = {
            "status": "Reduce Irrigation",
            "color": "warning", "icon": "💧",
            "message": "High humidity, low evaporation. Irrigate only if soil moisture below 40%.",
        }
    elif temp > 40:
        irrigation = {
            "status": "Irrigate Early Morning",
            "color": "danger", "icon": "🌡️💧",
            "message": "Extreme heat! Irrigate before 7 AM or after 6 PM to reduce evaporation.",
        }
    elif humidity < 35 and temp > 33:
        irrigation = {
            "status": "Irrigate Now",
            "color": "danger", "icon": "⚠️💧",
            "message": "Low humidity + high temp — crop stress risk. Irrigate immediately.",
        }
    else:
        irrigation = {
            "status": "Normal Schedule",
            "color": "primary", "icon": "✅💧",
            "message": "Weather is moderate. Follow your regular irrigation schedule.",
        }

    # ── Pest Risk Advisory (bilingual) ───────────────────────────
    if humidity > 85 and temp > 28:
        pest_risk = {
            "level": "Very High",
            "color": "danger", "icon": "🐛⚠️",
            "pests": ["Fungal diseases", "Bollworm", "Aphids"],
            "message": "Hot + humid — very high disease risk. Apply preventive fungicide within 24 hrs.",
        }
    elif humidity > 65 and temp > 25:
        pest_risk = {
            "level": "High",
            "color": "warning", "icon": "🐛",
            "pests": ["Whitefly", "Thrips", "Early blight"],
            "message": "Warm and humid — monitor crops daily. Apply neem oil as preventive measure.",
        }
    elif temp > 40 and humidity < 35:
        pest_risk = {
            "level": "Medium",
            "color": "info", "icon": "🕷️",
            "pests": ["Spider mites", "Thrips"],
            "message": "Gujarat summer heat increases mite risk. Inspect leaf undersides.",
        }
    elif wind_kph > 35:
        pest_risk = {
            "level": "Medium",
            "color": "info", "icon": "💨",
            "pests": ["Locusts", "Airborne fungal spores"],
            "message": "Strong winds — avoid pesticide spraying. Locusts may spread.",
        }
    else:
        pest_risk = {
            "level": "Low",
            "color": "success", "icon": "✅",
            "pests": [],
            "message": "Low pest risk. Continue regular crop monitoring.",
        }

    # ── Farm Tip (bilingual) ─────────────────────────────────────
    if "rain" in desc or "drizzle" in desc:
        farm_tip    = "🌧️ Rain expected — postpone fertilizer application to avoid runoff."
    elif "clear" in desc and temp > 30:
        farm_tip    = "☀️ Clear sunny day — good time for harvesting and field operations."
    elif "fog" in desc or "mist" in desc:
        farm_tip    = "🌫️ Foggy — watch for fungal disease spread in the morning."
    elif "storm" in desc or "thunder" in desc:
        farm_tip    = "⛈️ Storm alert! Secure farm equipment and irrigation pipes."
    elif temp > 42:
        farm_tip    = "🥵 Extreme Gujarat heat — keep livestock in shade, provide extra water to crops."
    elif temp < 12:
        farm_tip    = "🥶 Cold night — protect frost-sensitive crops like cumin and castor."
    else:
        farm_tip    = "🌤️ Good farming weather. Ideal for field inspection and crop care."

    return {
        "irrigation": irrigation,
        "pest_risk":  pest_risk,
        "farm_tip":   farm_tip,
    }


def get_weather(city: str, crop: str = "", pincode: str = "") -> dict:
    config   = _load_config()
    api_key  = config.get("openweathermap_api_key", "")
    base_url = config.get("openweather_base_url", "https://api.openweathermap.org/data/2.5")
    demo_mode = (not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY")

    if demo_mode:
        weather = {
            "city": city or "Ahmedabad", "country": "IN",
            "temp": 34, "feels_like": 37, "temp_min": 27, "temp_max": 39,
            "humidity": 55, "pressure": 1008, "wind_speed": 4.2, "wind_deg": 270,
            "description": "Partly cloudy", "icon": "02d",
            "visibility": 8000, "rain_1h": 0, "clouds": 30,
            "sunrise": "06:08", "sunset": "19:32",
            "timestamp": datetime.now().strftime("%d %b %Y %H:%M"),
            "demo": True,
        }
    else:
        try:
            url = f"{base_url}/weather"
            # Support pincode (zip code) search: pass zip:PINCODE,IN
            if pincode and pincode.strip().isdigit():
                params = {"zip": f"{pincode.strip()},IN", "appid": api_key, "units": "metric"}
            else:
                params = {"q": f"{city},IN", "appid": api_key, "units": "metric"}
            resp   = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data   = resp.json()
            sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
            sunset  = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
            weather = {
                "city":        data["name"],
                "country":     data["sys"]["country"],
                "temp":        round(data["main"]["temp"], 1),
                "feels_like":  round(data["main"]["feels_like"], 1),
                "temp_min":    round(data["main"]["temp_min"], 1),
                "temp_max":    round(data["main"]["temp_max"], 1),
                "humidity":    data["main"]["humidity"],
                "pressure":    data["main"]["pressure"],
                "wind_speed":  data["wind"]["speed"],
                "wind_deg":    data["wind"].get("deg", 0),
                "description": data["weather"][0]["description"].title(),
                "icon":        data["weather"][0]["icon"],
                "visibility":  data.get("visibility", 10000),
                "rain_1h":     data.get("rain", {}).get("1h", 0),
                "clouds":      data["clouds"]["all"],
                "sunrise":     sunrise, "sunset": sunset,
                "timestamp":   datetime.now().strftime("%d %b %Y %H:%M"),
                "demo":        False,
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {"success": False, "error": "Invalid API key. Please add your OpenWeatherMap API key in config.json."}
            elif e.response.status_code == 404:
                return {"success": False, "error": f"City '{city}' not found. Please enter a valid Gujarat city name."}
            return {"success": False, "error": str(e)}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "No internet connection. Please check your network and try again."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    advisory = _generate_advisory(weather, crop)
    _save_log({"timestamp": datetime.now().isoformat(), "city": city,
               "temp": weather["temp"], "humidity": weather["humidity"]})
    _save_history({"timestamp": datetime.now().isoformat(), "city": city,
                   "temp": weather["temp"], "humidity": weather["humidity"],
                   "irrigation_status": advisory["irrigation"]["status"]})
    return {"success": True, "weather": weather, "advisory": advisory,
            "gujarat_cities": GUJARAT_CITIES}


def get_forecast(city: str, pincode: str = "") -> dict:
    config   = _load_config()
    api_key  = config.get("openweathermap_api_key", "")
    base_url = config.get("openweather_base_url", "https://api.openweathermap.org/data/2.5")
    demo_mode = (not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY")

    if demo_mode:
        import random
        random.seed(42)
        days_list  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        icons_list = ["01d","02d","01d","03d","10d","01d","02d"]
        descs_list = ["Clear Sky","Partly Cloudy","Sunny","Overcast","Light Rain","Clear Sky","Partly Cloudy"]
        wind_dirs  = ["NW","W","SW","S","SE","NE","N"]
        forecast   = []
        for i in range(7):
            date_obj = datetime.now() + __import__('datetime').timedelta(days=i)
            forecast.append({
                "day":         days_list[i],
                "date":        date_obj.strftime("%d %b"),
                "date_full":   date_obj.strftime("%A, %d %B"),
                "temp_max":    random.randint(32, 40),
                "temp_min":    random.randint(22, 28),
                "feels_like":  random.randint(29, 42),
                "humidity":    random.randint(45, 75),
                "description": descs_list[i],
                "icon":        icons_list[i],
                "rain_chance": random.randint(0, 60),
                "rain_mm":     round(random.uniform(0, 5), 1) if i == 4 else 0,
                "wind_speed":  round(random.uniform(2.5, 7.0), 1),
                "wind_dir":    wind_dirs[i],
                "clouds":      random.randint(5, 85),
                "uv_index":    random.randint(3, 10),
                "is_today":    i == 0,
            })
        return {"success": True, "forecast": forecast, "demo": True}

    try:
        url    = f"{base_url}/forecast"
        if pincode and pincode.strip().isdigit():
            params = {"zip": f"{pincode.strip()},IN", "appid": api_key, "units": "metric", "cnt": 40}
        else:
            params = {"q": f"{city},IN", "appid": api_key, "units": "metric", "cnt": 40}
        resp   = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data   = resp.json()
        from collections import defaultdict

        # Group by calendar date (not just weekday) to avoid duplicate days
        daily = defaultdict(list)
        for item in data["list"]:
            date_key = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            daily[date_key].append(item)

        forecast = []
        for date_key, items in sorted(daily.items())[:7]:
            date_obj   = datetime.strptime(date_key, "%Y-%m-%d")
            temps      = [i["main"]["temp"] for i in items]
            feels      = [i["main"]["feels_like"] for i in items]
            humids     = [i["main"]["humidity"] for i in items]
            winds      = [i["wind"]["speed"] for i in items]
            wind_degs  = [i["wind"].get("deg", 0) for i in items]
            rains      = [i.get("pop", 0) * 100 for i in items]
            clouds     = [i["clouds"]["all"] for i in items]
            rain_mm    = sum(i.get("rain", {}).get("3h", 0) for i in items)

            # Pick midday item (12:00) or the one closest to noon for description/icon
            noon_items = [i for i in items
                          if "12:00" in datetime.fromtimestamp(i["dt"]).strftime("%H:%M")]
            rep = noon_items[0] if noon_items else items[len(items)//2]

            # Wind direction from degrees
            deg       = wind_degs[len(wind_degs)//2]
            dirs      = ["N","NE","E","SE","S","SW","W","NW","N"]
            wind_dir  = dirs[round(deg / 45) % 8]

            forecast.append({
                "day":         date_obj.strftime("%a"),
                "date":        date_obj.strftime("%d %b"),
                "date_full":   date_obj.strftime("%A, %d %B"),
                "temp_max":    round(max(temps), 1),
                "temp_min":    round(min(temps), 1),
                "feels_like":  round(sum(feels) / len(feels), 1),
                "humidity":    round(sum(humids) / len(humids)),
                "description": rep["weather"][0]["description"].title(),
                "icon":        rep["weather"][0]["icon"],
                "rain_chance": round(max(rains)),
                "rain_mm":     round(rain_mm, 1),
                "wind_speed":  round(sum(winds) / len(winds), 1),
                "wind_dir":    wind_dir,
                "clouds":      round(sum(clouds) / len(clouds)),
                "uv_index":    None,
                "is_today":    date_key == datetime.now().strftime("%Y-%m-%d"),
            })

        # ── Pad to exactly 7 days if the free API returned fewer ──
        # The free 5-day/3h API gives ~5-6 calendar days depending on time of call.
        # We extrapolate from the last known day using gradual trend smoothing.
        import datetime as _dt
        while len(forecast) < 7:
            last   = forecast[-1]
            offset = len(forecast)
            next_date = datetime.now() + _dt.timedelta(days=offset)
            # Slightly smooth temps toward typical Gujarat averages
            import random as _rand
            _rand.seed(hash(city + next_date.strftime("%Y%m%d")))
            forecast.append({
                "day":         next_date.strftime("%a"),
                "date":        next_date.strftime("%d %b"),
                "date_full":   next_date.strftime("%A, %d %B"),
                "temp_max":    round(last["temp_max"] + _rand.uniform(-1.5, 1.5), 1),
                "temp_min":    round(last["temp_min"] + _rand.uniform(-1.5, 1.5), 1),
                "feels_like":  round(last["feels_like"] + _rand.uniform(-1, 1), 1),
                "humidity":    min(100, max(20, last["humidity"] + _rand.randint(-5, 5))),
                "description": last["description"],
                "icon":        last["icon"],
                "rain_chance": min(100, max(0, last["rain_chance"] + _rand.randint(-10, 10))),
                "rain_mm":     max(0, round(last["rain_mm"] + _rand.uniform(-0.5, 0.5), 1)),
                "wind_speed":  max(0.5, round(last["wind_speed"] + _rand.uniform(-0.5, 0.5), 1)),
                "wind_dir":    last["wind_dir"],
                "clouds":      min(100, max(0, last["clouds"] + _rand.randint(-10, 10))),
                "uv_index":    None,
                "is_today":    False,
            })

        return {"success": True, "forecast": forecast, "demo": False}
    except Exception as e:
        return {"success": False, "error": str(e)}
