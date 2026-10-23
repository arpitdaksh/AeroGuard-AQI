"""
Machine Learning Inference Engine.
Loads serialized models and provides real-time AQI prediction, category classification,
probability distribution, and future 24-hr forecast simulation.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
try:
    from src.aqi_calculator import calculate_overall_aqi, get_aqi_category, generate_activity_advice
except ImportError:
    from aqi_calculator import calculate_overall_aqi, get_aqi_category, generate_activity_advice

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
REGRESSOR_PATH = os.path.join(MODEL_DIR, "aqi_regressor.joblib")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "aqi_classifier.joblib")

_regressor = None
_classifier = None

def _get_models():
    global _regressor, _classifier
    if _regressor is None and os.path.exists(REGRESSOR_PATH):
        _regressor = joblib.load(REGRESSOR_PATH)
    if _classifier is None and os.path.exists(CLASSIFIER_PATH):
        _classifier = joblib.load(CLASSIFIER_PATH)
    return _regressor, _classifier

def predict_aqi(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs ML regression and classification on the input atmospheric features.
    """
    regressor, classifier = _get_models()

    now = datetime.now()
    hour = int(features.get("hour", now.hour))
    month = int(features.get("month", now.month))

    pm25 = float(features.get("pm25", 45.0))
    pm10 = float(features.get("pm10", 85.0))
    no2 = float(features.get("no2", 30.0))
    so2 = float(features.get("so2", 15.0))
    co = float(features.get("co", 1.0))
    # Open-Meteo CO normalization
    if co > 50:
        co = round(co / 1000.0, 2)
    o3 = float(features.get("o3", 35.0))
    nh3 = float(features.get("nh3", 20.0))

    temp = float(features.get("temperature", 25.0))
    humidity = float(features.get("humidity", 60.0))
    wind_speed = float(features.get("wind_speed", 3.0))
    rainfall = float(features.get("rainfall", 0.0))
    pressure = float(features.get("pressure", 1012.0))

    # Standard CPCB baseline calculation
    deterministic_res = calculate_overall_aqi({
        "pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co, "o3": o3, "nh3": nh3
    })

    input_df = pd.DataFrame([{
        "pm25": pm25,
        "pm10": pm10,
        "no2": no2,
        "so2": so2,
        "co": co,
        "o3": o3,
        "nh3": nh3,
        "temperature": temp,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "rainfall": rainfall,
        "pressure": pressure,
        "hour": hour,
        "month": month,
    }])

    if regressor is not None and classifier is not None:
        predicted_aqi = float(regressor.predict(input_df)[0])
        predicted_category = str(classifier.predict(input_df)[0])
        
        # Class probabilities
        probs = classifier.predict_proba(input_df)[0]
        prob_dict = {
            cls_name: round(float(prob) * 100, 1)
            for cls_name, prob in zip(classifier.classes_, probs)
        }
    else:
        # Fallback to formula
        predicted_aqi = float(deterministic_res["aqi"])
        predicted_category = deterministic_res["category_info"]["category"]
        prob_dict = {predicted_category: 100.0}

    category_info = get_aqi_category(predicted_aqi)

    # 24-Hour ML Simulation Forecast
    forecast_24h = []
    if regressor is not None:
        for offset in range(1, 25):
            sim_time = now.hour + offset
            sim_hour = sim_time % 24
            
            # Simulated diurnal weather fluctuation
            sim_temp = temp + 4.0 * np.sin((sim_hour - 8) * np.pi / 12)
            sim_humidity = max(20.0, min(95.0, humidity - 10.0 * np.sin((sim_hour - 8) * np.pi / 12)))
            sim_wind = max(0.5, wind_speed + 1.2 * np.cos(sim_hour * np.pi / 12))
            
            # Traffic rush adjustments
            rush = 1.3 if (8 <= sim_hour <= 10 or 18 <= sim_hour <= 21) else (0.8 if 1 <= sim_hour <= 5 else 1.0)
            sim_pm25 = max(5.0, pm25 * rush * (3.0 / sim_wind) ** 0.3)
            sim_pm10 = max(10.0, pm10 * rush * (3.0 / sim_wind) ** 0.3)

            sim_row = pd.DataFrame([{
                "pm25": sim_pm25,
                "pm10": sim_pm10,
                "no2": no2 * rush,
                "so2": so2,
                "co": co * rush,
                "o3": o3,
                "nh3": nh3,
                "temperature": sim_temp,
                "humidity": sim_humidity,
                "wind_speed": sim_wind,
                "rainfall": rainfall,
                "pressure": pressure,
                "hour": sim_hour,
                "month": month,
            }])

            f_aqi = round(float(regressor.predict(sim_row)[0]))
            forecast_24h.append({
                "hour": f"{sim_hour:02d}:00",
                "predicted_aqi": f_aqi,
                "category": get_aqi_category(f_aqi)["category"],
                "color": get_aqi_category(f_aqi)["color"],
            })

    activity_name = features.get("activity", "general outdoor activity")
    activity_advice = generate_activity_advice(predicted_aqi, activity_name, pm25, pm10)

    return {
        "predicted_aqi": round(predicted_aqi),
        "predicted_category": predicted_category,
        "category_info": category_info,
        "calculated_cpcb_aqi": deterministic_res["aqi"],
        "dominant_pollutant": deterministic_res["dominant_pollutant"],
        "sub_indices": deterministic_res["sub_indices"],
        "category_probabilities": prob_dict,
        "activity_advice": activity_advice,
        "forecast_24h": forecast_24h,
    }
