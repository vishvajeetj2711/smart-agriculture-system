"""
Solar Panel Income Estimator Module
Calculates solar income, farming income, and suggests optimal
land split between farming and solar panels.
"""

import os
import json
from datetime import datetime

BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_JSON    = os.path.join(BASE_DIR, "config.json")
SOLAR_CFG_JSON = os.path.join(BASE_DIR, "data", "solar_config.json")
RECORDS_JSON   = os.path.join(BASE_DIR, "data", "solar_records.json")
HISTORY_JSON   = os.path.join(BASE_DIR, "data", "user_history.json")


def _load_config():
    with open(CONFIG_JSON, "r") as f:
        return json.load(f)


def _load_solar_config():
    with open(SOLAR_CFG_JSON, "r") as f:
        return json.load(f)


def _save_record(entry: dict):
    with open(RECORDS_JSON, "r", encoding="utf-8") as f:
        records = json.load(f)
    records.append(entry)
    records = records[-100:]
    with open(RECORDS_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def _save_history(entry: dict):
    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        history = json.load(f)
    history["solar_estimates"].append(entry)
    history["solar_estimates"] = history["solar_estimates"][-50:]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def calculate_solar_income(total_land_acres: float,
                            solar_land_acres: float,
                            rate_per_kwh: float,
                            sunlight_hours: float,
                            crop: str = "Other",
                            subsidy_pct: float = 0.30) -> dict:
    """
    Calculate solar panel installation details and projected income.
    Returns detailed breakdown for farmer decision making.
    """
    solar_cfg   = _load_solar_config()

    panel_watt          = solar_cfg["panel_watt"]           # 400W
    panel_area_sqm      = solar_cfg["panel_area_sqm"]       # 2 m²
    panel_cost_inr      = solar_cfg["panel_cost_inr"]       # ₹25,000
    install_cost_panel  = solar_cfg["installation_cost_per_panel_inr"]  # ₹5,000
    maint_pct           = solar_cfg["maintenance_annual_pct"]           # 2%
    system_efficiency   = solar_cfg["system_efficiency"]                # 80%
    panels_per_acre     = solar_cfg["panels_per_acre"]                  # 200

    crop_income_map     = solar_cfg.get("avg_crop_income_per_acre_inr", {})
    crop_income_per_acre= crop_income_map.get(crop, crop_income_map.get("Other", 35000))

    # ── Solar calculations ───────────────────────────────────────
    farming_land_acres  = total_land_acres - solar_land_acres
    num_panels          = int(solar_land_acres * panels_per_acre)
    if num_panels < 1:
        num_panels = 1

    total_kw            = num_panels * panel_watt / 1000   # kW installed

    # Daily energy generation
    daily_kwh           = total_kw * sunlight_hours * system_efficiency
    monthly_kwh         = daily_kwh * 30
    annual_kwh          = daily_kwh * 365

    # Income
    monthly_income_inr  = monthly_kwh * rate_per_kwh
    annual_income_inr   = annual_kwh  * rate_per_kwh

    # Cost
    hardware_cost       = num_panels * panel_cost_inr
    installation_cost   = num_panels * install_cost_panel
    total_cost          = hardware_cost + installation_cost
    subsidy_amount      = total_cost * subsidy_pct
    net_cost            = total_cost - subsidy_amount
    annual_maintenance  = net_cost * maint_pct
    net_annual_income   = annual_income_inr - annual_maintenance

    # Payback period
    payback_years       = round(net_cost / net_annual_income, 1) if net_annual_income > 0 else 99

    # Farming income
    farming_annual_income = farming_land_acres * crop_income_per_acre

    # Total combined income
    total_annual_income   = net_annual_income + farming_annual_income

    # ── Optimal split calculation ────────────────────────────────
    # Find best split that maximizes total income
    best_total = 0
    best_solar_acres = solar_land_acres
    best_farming_acres = farming_land_acres

    for trial_solar in [i * 0.25 for i in range(0, int(total_land_acres / 0.25) + 1)]:
        if trial_solar > total_land_acres:
            break
        trial_farming = total_land_acres - trial_solar
        trial_panels  = int(trial_solar * panels_per_acre)
        if trial_panels < 1 and trial_solar > 0:
            continue

        t_kwh     = trial_panels * panel_watt / 1000 * sunlight_hours * system_efficiency * 365
        t_solar_Y = t_kwh * rate_per_kwh
        t_farm_Y  = trial_farming * crop_income_per_acre
        t_total   = t_solar_Y + t_farm_Y

        if t_total > best_total:
            best_total         = t_total
            best_solar_acres   = trial_solar
            best_farming_acres = trial_farming

    # Is all solar better?
    all_solar_panels  = int(total_land_acres * panels_per_acre)
    all_solar_annual  = (all_solar_panels * panel_watt / 1000 *
                         sunlight_hours * system_efficiency * 365 * rate_per_kwh)
    all_farm_annual   = total_land_acres * crop_income_per_acre

    if all_solar_annual > all_farm_annual * 1.3:
        optimal_note = f"Solar energy is significantly more profitable for your land. Consider allocating {min(total_land_acres * 0.5, 5):.1f} acres to solar."
    elif all_farm_annual > all_solar_annual * 1.3:
        optimal_note = f"Farming is more profitable for {crop}. Keep most land for farming and use a small portion for solar."
    else:
        optimal_note = f"Mixed approach recommended: {best_solar_acres:.1f} acres solar + {best_farming_acres:.1f} acres farming for maximum income."

    # ── Savings vs pure farming ──────────────────────────────────
    pure_farm_income = total_land_acres * crop_income_per_acre
    extra_income     = total_annual_income - pure_farm_income

    result = {
        "success":               True,
        "input": {
            "total_land":        total_land_acres,
            "solar_land":        solar_land_acres,
            "farming_land":      round(farming_land_acres, 2),
            "rate_per_kwh":      rate_per_kwh,
            "sunlight_hours":    sunlight_hours,
            "crop":              crop,
        },
        "solar": {
            "num_panels":        num_panels,
            "total_kw":          round(total_kw, 2),
            "daily_kwh":         round(daily_kwh, 1),
            "monthly_kwh":       round(monthly_kwh, 1),
            "annual_kwh":        round(annual_kwh, 1),
            "monthly_income":    round(monthly_income_inr),
            "annual_income":     round(annual_income_inr),
            "annual_maintenance":round(annual_maintenance),
            "net_annual_income": round(net_annual_income),
        },
        "cost": {
            "hardware_cost":     round(hardware_cost),
            "installation_cost": round(installation_cost),
            "total_cost":        round(total_cost),
            "subsidy_amount":    round(subsidy_amount),
            "net_cost":          round(net_cost),
            "payback_years":     payback_years,
        },
        "farming": {
            "land_acres":        round(farming_land_acres, 2),
            "crop":              crop,
            "annual_income":     round(farming_annual_income),
            "income_per_acre":   crop_income_per_acre,
        },
        "combined": {
            "total_annual_income": round(total_annual_income),
            "monthly_income":      round(total_annual_income / 12),
            "extra_vs_farming":    round(extra_income),
            "extra_pct":           round(extra_income / pure_farm_income * 100, 1) if pure_farm_income > 0 else 0,
        },
        "optimal": {
            "solar_acres":    best_solar_acres,
            "farming_acres":  round(best_farming_acres, 2),
            "total_income":   round(best_total),
            "note":           optimal_note,
        },
        "govt_info": {
            "pm_kusum_scheme": "PM-KUSUM scheme provides 30% central subsidy on solar pump and power generation.",
            "net_metering":    "Net metering allows you to sell surplus solar power to DISCOM at government rate.",
            "helpline":        "MNRE Helpline: 1800-180-3333 (Toll-Free)",
        }
    }

    _save_record({
        "timestamp":      datetime.now().isoformat(),
        "total_land":     total_land_acres,
        "solar_land":     solar_land_acres,
        "num_panels":     num_panels,
        "monthly_income": round(monthly_income_inr),
        "annual_income":  round(annual_income_inr),
        "payback_years":  payback_years,
    })
    _save_history({
        "timestamp":     datetime.now().isoformat(),
        "solar_land":    solar_land_acres,
        "num_panels":    num_panels,
        "annual_income": round(annual_income_inr),
    })

    return result
