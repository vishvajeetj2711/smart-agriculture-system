"""
Daily WhatsApp Price Alert Sender
===================================
Run this script once daily (via Task Scheduler / cron):

  python modules/send_daily_alerts.py

What it does:
  1. Reads all active subscribers from data/whatsapp_alerts.json
  2. Groups them by crop
  3. Fetches latest Gujarat mandi price for each crop
  4. Sends personalised WhatsApp message to each subscriber
  5. Logs results to data/alert_send_log.json

Schedule on Windows Task Scheduler:
  Action : python "C:\\Users\\vishv\\smart_agriculture\\modules\\send_daily_alerts.py"
  Trigger: Daily at 08:00 AM
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict

# Make sure project root is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from modules.whatsapp_alerts import (
    get_all_active_subscribers,
    send_price_alert,
    _load_db, _save_db,
)
from modules.market_prices import get_market_prices

LOG_FILE = os.path.join(BASE_DIR, "data", "alert_send_log.json")


def _load_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_log(entries: list):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries[-500:], f, indent=2, ensure_ascii=False)  # keep last 500


def run_daily_alerts():
    print("=" * 55)
    print(f"  Smart Agriculture — WhatsApp Daily Alert Sender")
    print(f"  {datetime.now().strftime('%d %B %Y  %H:%M:%S')}")
    print("=" * 55)

    subscribers = get_all_active_subscribers()
    if not subscribers:
        print("  No active subscribers. Nothing to send.")
        return

    print(f"  Active subscribers: {len(subscribers)}")

    # Group subscribers by crop to minimise API calls
    crop_groups = defaultdict(list)
    for sub in subscribers:
        crop_groups[sub["crop"]].append(sub)

    print(f"  Unique crops: {list(crop_groups.keys())}\n")

    log      = _load_log()
    run_log  = {
        "run_at":    datetime.now().isoformat(),
        "total":     len(subscribers),
        "sent":      0,
        "failed":    0,
        "skipped":   0,
        "details":   [],
    }

    for crop, subs in crop_groups.items():
        print(f"  Fetching price for: {crop}...")

        # Fetch price for default district — Ahmedabad
        price_data = get_market_prices(crop, "Ahmedabad")
        prices     = price_data.get("prices", []) if price_data.get("success") else []

        if not prices:
            print(f"    ⚠️  No price data for {crop} — skipping {len(subs)} subscribers")
            for sub in subs:
                run_log["skipped"] += 1
                run_log["details"].append({
                    "number": sub["whatsapp_number"],
                    "crop":   crop,
                    "status": "skipped",
                    "reason": "No price data",
                })
            continue

        best_price = prices[0]["modal_price"]
        print(f"    Best price: ₹{best_price:,}/qtl at {prices[0]['market']}")

        for sub in subs:
            result = send_price_alert(sub, prices)
            number_display = sub["whatsapp_number"][-4:].rjust(14, "*")

            if result.get("success"):
                run_log["sent"] += 1
                status = "sent_demo" if result.get("demo") else "sent"
                print(f"    ✅ {number_display} — {status}")
            else:
                run_log["failed"] += 1
                status = "failed"
                print(f"    ❌ {number_display} — {result.get('error', 'Unknown error')}")

            run_log["details"].append({
                "number":    sub["whatsapp_number"],
                "crop":      crop,
                "price":     best_price,
                "market":    prices[0]["market"],
                "status":    status,
                "timestamp": datetime.now().isoformat(),
            })

    # Save run timestamp to main DB
    db = _load_db()
    db["last_daily_run"] = datetime.now().isoformat()
    _save_db(db)

    # Append to log
    log.append(run_log)
    _save_log(log)

    print(f"\n  Summary: {run_log['sent']} sent | "
          f"{run_log['failed']} failed | {run_log['skipped']} skipped")
    print("=" * 55)
    return run_log


if __name__ == "__main__":
    run_daily_alerts()
