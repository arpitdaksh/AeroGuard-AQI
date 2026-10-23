"""
Air Quality Index (AQI) Breakpoint Calculator.
Implements official Indian CPCB (Central Pollution Control Board) and US EPA standards.
"""

from typing import Dict, Any, Optional, Tuple

# CPCB Breakpoints: (C_low, C_high, I_low, I_high)
# Units: PM2.5, PM10, NO2, SO2, O3, NH3 are in µg/m3; CO is in mg/m3
CPCB_BREAKPOINTS = {
    "pm25": [
        (0.0, 30.0, 0, 50),
        (30.1, 60.0, 51, 100),
        (60.1, 90.0, 101, 200),
        (90.1, 120.0, 201, 300),
        (120.1, 250.0, 301, 400),
        (250.1, 500.0, 401, 500),
    ],
    "pm10": [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 250.0, 101, 200),
        (250.1, 350.0, 201, 300),
        (350.1, 430.0, 301, 400),
        (430.1, 600.0, 401, 500),
    ],
    "no2": [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 180.0, 101, 200),
        (180.1, 280.0, 201, 300),
        (280.1, 400.0, 301, 400),
        (400.1, 800.0, 401, 500),
    ],
    "so2": [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 380.0, 101, 200),
        (380.1, 800.0, 201, 300),
        (800.1, 1600.0, 301, 400),
        (1600.1, 2400.0, 401, 500),
    ],
    "co": [  # In mg/m³
        (0.0, 1.0, 0, 50),
        (1.01, 2.0, 51, 100),
        (2.01, 10.0, 101, 200),
        (10.01, 17.0, 201, 300),
        (17.01, 34.0, 301, 400),
        (34.01, 50.0, 401, 500),
    ],
    "o3": [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 168.0, 101, 200),
        (168.1, 208.0, 201, 300),
        (208.1, 748.0, 301, 400),
        (748.1, 1000.0, 401, 500),
    ],
    "nh3": [
        (0.0, 200.0, 0, 50),
        (200.1, 400.0, 51, 100),
        (400.1, 800.0, 101, 200),
        (800.1, 1200.0, 201, 300),
        (1200.1, 1800.0, 301, 400),
        (1800.1, 2400.0, 401, 500),
    ],
}

# US EPA Breakpoints: (C_low, C_high, I_low, I_high)
EPA_BREAKPOINTS = {
    "pm25": [  # µg/m³
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ],
    "pm10": [  # µg/m³
        (0.0, 54.0, 0, 50),
        (55.0, 154.0, 51, 100),
        (155.0, 254.0, 101, 150),
        (255.0, 354.0, 151, 200),
        (355.0, 424.0, 201, 300),
        (425.0, 604.0, 301, 500),
    ],
    "o3": [  # µg/m³
        (0.0, 108.0, 0, 50),
        (109.0, 140.0, 51, 100),
        (141.0, 170.0, 101, 150),
        (171.0, 210.0, 151, 200),
        (211.0, 400.0, 201, 300),
        (401.0, 800.0, 301, 500),
    ],
    "co": [  # mg/m³
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ],
    "so2": [  # µg/m³
        (0.0, 92.0, 0, 50),
        (93.0, 196.0, 51, 100),
        (197.0, 485.0, 101, 150),
        (486.0, 797.0, 151, 200),
        (798.0, 1583.0, 201, 300),
        (1584.0, 2630.0, 301, 500),
    ],
    "no2": [  # µg/m³
        (0.0, 100.0, 0, 50),
        (101.0, 188.0, 51, 100),
        (189.0, 677.0, 101, 150),
        (678.0, 1221.0, 151, 200),
        (1222.0, 2349.0, 201, 300),
        (2350.0, 3849.0, 301, 500),
    ],
}

def calculate_sub_index(pollutant: str, concentration: float, standard: str = "CPCB") -> float:
    """
    Computes linear interpolation sub-index for a given pollutant.
    Formula: Ip = [(I_hi - I_lo) / (BP_hi - BP_lo)] * (Cp - BP_lo) + I_lo
    """
    pollutant = pollutant.lower().replace(".", "").replace("-", "")
    breakpoints_table = CPCB_BREAKPOINTS if standard.upper() == "CPCB" else EPA_BREAKPOINTS

    if pollutant not in breakpoints_table or concentration < 0:
        return 0.0

    table = breakpoints_table[pollutant]

    for c_lo, c_hi, i_lo, i_hi in table:
        if c_lo <= concentration <= c_hi:
            sub_index = ((i_hi - i_lo) / (c_hi - c_lo)) * (concentration - c_lo) + i_lo
            return round(sub_index, 1)

    c_lo, c_hi, i_lo, i_hi = table[-1]
    if concentration > c_hi:
        sub_index = ((i_hi - i_lo) / (c_hi - c_lo)) * (concentration - c_lo) + i_lo
        return min(round(sub_index, 1), 500.0)

    return 0.0

def get_aqi_category(aqi_value: float, standard: str = "CPCB") -> Dict[str, Any]:
    """
    Returns category name, color codes, health impact, and fitness advisories.
    """
    aqi_round = round(aqi_value)
    
    if standard.upper() == "EPA":
        if aqi_round <= 50:
            return {
                "category": "Good",
                "color": "#10b981",
                "bg_class": "bg-emerald-500",
                "text_class": "text-emerald-700",
                "border_class": "border-emerald-500",
                "shadow_class": "shadow-emerald-500/40",
                "health_impact": "Air quality is considered satisfactory, and air pollution poses little or no risk.",
                "mask_recommended": False,
                "outdoor_activity": "Ideal for all outdoor activities and vigorous sports.",
            }
        elif aqi_round <= 100:
            return {
                "category": "Moderate",
                "color": "#f59e0b",
                "bg_class": "bg-amber-400",
                "text_class": "text-amber-700",
                "border_class": "border-amber-400",
                "shadow_class": "shadow-amber-400/40",
                "health_impact": "Air quality is acceptable; however, some pollutants may cause moderate health concern for sensitive individuals.",
                "mask_recommended": False,
                "outdoor_activity": "Safe for healthy individuals; sensitive people should reduce prolonged exertion.",
            }
        elif aqi_round <= 150:
            return {
                "category": "Unhealthy for Sensitive Groups",
                "color": "#f97316",
                "bg_class": "bg-orange-500",
                "text_class": "text-orange-700",
                "border_class": "border-orange-500",
                "shadow_class": "shadow-orange-500/40",
                "health_impact": "Members of sensitive groups may experience health effects. General public is less likely to be affected.",
                "mask_recommended": True,
                "outdoor_activity": "Sensitive groups should shift workouts indoors; others can proceed normally.",
            }
        elif aqi_round <= 200:
            return {
                "category": "Unhealthy",
                "color": "#ef4444",
                "bg_class": "bg-rose-500",
                "text_class": "text-rose-700",
                "border_class": "border-rose-500",
                "shadow_class": "shadow-rose-500/40",
                "health_impact": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious effects.",
                "mask_recommended": True,
                "outdoor_activity": "Avoid intense outdoor cardio or running; prefer indoor gym sessions.",
            }
        elif aqi_round <= 300:
            return {
                "category": "Very Unhealthy",
                "color": "#9333ea",
                "bg_class": "bg-purple-600",
                "text_class": "text-purple-700",
                "border_class": "border-purple-600",
                "shadow_class": "shadow-purple-600/40",
                "health_impact": "Health alert: The risk of health effects is increased for everyone.",
                "mask_recommended": True,
                "outdoor_activity": "Move all activities indoors. Use HEPA air purifiers.",
            }
        else:
            return {
                "category": "Hazardous",
                "color": "#881337",
                "bg_class": "bg-rose-950",
                "text_class": "text-rose-950",
                "border_class": "border-rose-950",
                "shadow_class": "shadow-rose-950/40",
                "health_impact": "Emergency conditions: The entire population is likely to be affected.",
                "mask_recommended": True,
                "outdoor_activity": "Remain indoors with doors/windows sealed. No outdoor exertion.",
            }

    # CPCB (Indian Standard)
    if aqi_round <= 50:
        return {
            "category": "Good",
            "color": "#10b981",
            "bg_class": "bg-emerald-500",
            "text_class": "text-emerald-700",
            "border_class": "border-emerald-500",
            "shadow_class": "shadow-emerald-500/40",
            "health_impact": "Minimal impact. Clean and safe air.",
            "mask_recommended": False,
            "outdoor_activity": "Enjoy outdoor sports, running, cycling, and weight training outside.",
        }
    elif aqi_round <= 100:
        return {
            "category": "Satisfactory",
            "color": "#84cc16",
            "bg_class": "bg-lime-500",
            "text_class": "text-lime-700",
            "border_class": "border-lime-500",
            "shadow_class": "shadow-lime-500/40",
            "health_impact": "Minor breathing discomfort to sensitive people.",
            "mask_recommended": False,
            "outdoor_activity": "Safe for regular physical workouts and outdoor sports.",
        }
    elif aqi_round <= 200:
        return {
            "category": "Moderate",
            "color": "#eab308",
            "bg_class": "bg-yellow-500",
            "text_class": "text-yellow-700",
            "border_class": "border-yellow-500",
            "shadow_class": "shadow-yellow-500/40",
            "health_impact": "Breathing discomfort to people with lung, asthma, and heart diseases.",
            "mask_recommended": False,
            "outdoor_activity": "Take intermittent breaks during intense cardio. Sensitive groups should wear N95 outdoors.",
        }
    elif aqi_round <= 300:
        return {
            "category": "Poor",
            "color": "#f97316",
            "bg_class": "bg-orange-500",
            "text_class": "text-orange-700",
            "border_class": "border-orange-500",
            "shadow_class": "shadow-orange-500/40",
            "health_impact": "Breathing discomfort to most people on prolonged exposure.",
            "mask_recommended": True,
            "outdoor_activity": "Avoid early morning outdoor running/jogging when particulate inversion peaks. Prefer indoor gym.",
        }
    elif aqi_round <= 400:
        return {
            "category": "Very Poor",
            "color": "#ef4444",
            "bg_class": "bg-red-600",
            "text_class": "text-red-700",
            "border_class": "border-red-600",
            "shadow_class": "shadow-red-600/40",
            "health_impact": "Respiratory illness on prolonged exposure. Pronounced effect on people with lung and heart diseases.",
            "mask_recommended": True,
            "outdoor_activity": "Strictly avoid outdoor cardiovascular exercises. Wear N95/N99 respirators when stepping out.",
        }
    else:
        return {
            "category": "Severe",
            "color": "#7f1d1d",
            "bg_class": "bg-red-950",
            "text_class": "text-red-950",
            "border_class": "border-red-950",
            "shadow_class": "shadow-red-950/40",
            "health_impact": "Affects healthy people and seriously impacts those with existing diseases. Emergency condition.",
            "mask_recommended": True,
            "outdoor_activity": "Stay indoors, keep air purifiers on high. Do light indoor stretching only.",
        }

def calculate_overall_aqi(pollutants: Dict[str, float], standard: str = "CPCB") -> Dict[str, Any]:
    """
    Computes overall AQI from a dictionary of pollutants.
    Expected keys: pm25, pm10, no2, so2, co, o3, nh3.
    """
    sub_indices: Dict[str, float] = {}
    normalized = {}

    for k, v in pollutants.items():
        if v is None:
            continue
        try:
            val = float(v)
        except (ValueError, TypeError):
            continue

        clean_key = k.lower().replace(".", "").replace("-", "")
        # Auto-convert CO from µg/m³ to mg/m³ if it exceeds 50
        if clean_key == "co" and val > 50.0:
            val = round(val / 1000.0, 3)

        normalized[clean_key] = val
        sub_index = calculate_sub_index(clean_key, val, standard=standard)
        sub_indices[clean_key] = sub_index

    if not sub_indices:
        return {
            "aqi": 0.0,
            "dominant_pollutant": "None",
            "category_info": get_aqi_category(0, standard),
            "sub_indices": {},
            "pollutant_values": {},
        }

    dominant_pollutant, max_sub_index = max(sub_indices.items(), key=lambda item: item[1])
    category_info = get_aqi_category(max_sub_index, standard=standard)

    return {
        "aqi": round(max_sub_index),
        "dominant_pollutant": dominant_pollutant.upper(),
        "category_info": category_info,
        "sub_indices": sub_indices,
        "pollutant_values": normalized,
    }

def generate_activity_advice(aqi: float, activity: str, pm25: float, pm10: float) -> str:
    """
    Generates intelligent activity-specific health recommendations based on AQI and pollutants.
    """
    cat = get_aqi_category(aqi)["category"]
    activity_clean = (activity or "general activity").strip().lower()

    bullet_points = []
    is_cardio = any(w in activity_clean for w in ["run", "jog", "sprint", "cardio", "cycle", "cycling", "football", "marathon", "hiit"])
    is_outdoor = any(w in activity_clean for w in ["outdoor", "park", "road", "walk", "street"])

    if aqi <= 50:
        bullet_points.append(f"Air quality is Good ({cat}). It is completely safe and optimal for '{activity}'.")
        bullet_points.append("Your respiratory intake will experience clean ambient air with no protective gear required.")
        bullet_points.append("Enjoy extended outdoor cardio, stamina training, or sports without restrictions.")
    elif aqi <= 100:
        bullet_points.append(f"Current AQI is Satisfactory/Moderate ({round(aqi)}). Proceed with '{activity}'.")
        if is_cardio:
            bullet_points.append("Vigorous aerobic training is safe; hydrate well and monitor if you have mild asthma.")
        else:
            bullet_points.append("Normal physical routines and strength training can be conducted outdoors or indoors.")
        bullet_points.append("No specialized respirator is needed for the general population.")
    elif aqi <= 200:
        bullet_points.append(f"AQI is Moderately Polluted ({round(aqi)}). Particulate concentration (PM2.5: {pm25} µg/m³) is elevated.")
        if is_cardio or is_outdoor:
            bullet_points.append(f"Shift '{activity}' indoors if possible, or schedule it during afternoon hours when smog clears.")
        else:
            bullet_points.append("Indoor workouts (like gym and weight training) are preferred over outdoor activities.")
        bullet_points.append("Sensitive individuals and asthmatics should keep inhalers on hand and limit session duration to under 45 minutes.")
    elif aqi <= 300:
        bullet_points.append(f"AQI is in the Poor range ({round(aqi)}). Significant fine particulate matter detected (PM2.5: {pm25} µg/m³).")
        if is_cardio:
            bullet_points.append("Strictly avoid outdoor cardiovascular training (running, cycling) as deep lung inhalation will absorb micro-particulates.")
        else:
            bullet_points.append(f"Conduct '{activity}' inside an air-conditioned or air-purified fitness space.")
        bullet_points.append("Wear a certified N95 / FFP2 mask if you need to step outside to commute to your workout.")
    elif aqi <= 400:
        bullet_points.append(f"AQI is Very Poor ({round(aqi)}). Ambient air poses significant health risks to the respiratory and vascular systems.")
        bullet_points.append(f"Replace high-intensity '{activity}' with low-intensity indoor bodyweight movements or gentle stretching.")
        bullet_points.append("Keep indoor HEPA air purifiers operating on high, seal windows, and strictly wear N95/N99 when outside.")
    else:
        bullet_points.append(f"CRITICAL: AQI is Severe / Hazardous ({round(aqi)}). Emergency smog levels present (PM2.5: {pm25} µg/m³).")
        bullet_points.append("Cease all strenuous exertion and workouts. Elevated breathing rates drastically amplify particulate absorption.")
        bullet_points.append("Remain in an enclosed, purified indoor room. Anyone experiencing chest tightness or shortness of breath should seek medical advice.")

    return "\n".join(f"• {bp}" for bp in bullet_points)

