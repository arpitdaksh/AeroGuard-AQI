"""
Air Quality Index (AQI) Web Application & RESTful API Backend.
Serves interactive dashboard, real-time predictions, standard CPCB/EPA calculations,
live atmospheric lookups, and model telemetry.
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from src.aqi_calculator import calculate_overall_aqi, get_aqi_category, generate_activity_advice
from src.live_api import fetch_live_air_quality
from src.predictor import predict_aqi

app = Flask(__name__)
CORS(app)

METRICS_PATH = os.path.join(os.path.dirname(__file__), "models", "metrics.json")
HISTORICAL_PATH = os.path.join(os.path.dirname(__file__), "data", "city_aqi_historical.csv")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/live", methods=["GET"])
def api_live():
    """
    Returns real-time air quality & weather for any city worldwide.
    Query param: city (default: 'Panipat')
    Query param: standard ('CPCB' or 'EPA', default: 'CPCB')
    """
    city = request.args.get("city", "Panipat")
    standard = request.args.get("standard", "CPCB").upper()
    data = fetch_live_air_quality(city, standard=standard)
    
    # Add smart activity advice
    activity = request.args.get("activity", "outdoor running")
    advice = generate_activity_advice(
        data["aqi"],
        activity,
        data["pollutants"].get("pm25", 0),
        data["pollutants"].get("pm10", 0),
    )
    data["activity_advice"] = advice
    return jsonify(data)

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Runs ML regression and classification on user-provided pollutant & weather values.
    """
    payload = request.get_json(force=True, silent=True) or {}
    result = predict_aqi(payload)
    return jsonify(result)

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    Pure mathematical breakpoint calculation adhering strictly to CPCB or EPA standards.
    """
    payload = request.get_json(force=True, silent=True) or {}
    standard = payload.get("standard", "CPCB").upper()
    pollutants = payload.get("pollutants", payload)
    
    result = calculate_overall_aqi(pollutants, standard=standard)
    return jsonify(result)

@app.route("/api/advice", methods=["POST"])
def api_advice():
    """
    Generates intelligent activity and health recommendations.
    """
    payload = request.get_json(force=True, silent=True) or {}
    aqi = float(payload.get("aqi", 150))
    activity = payload.get("activity", "workout")
    pm25 = float(payload.get("pm25", 50))
    pm10 = float(payload.get("pm10", 100))
    
    advice = generate_activity_advice(aqi, activity, pm25, pm10)
    category_info = get_aqi_category(aqi)
    return jsonify({
        "aqi": aqi,
        "activity": activity,
        "advice": advice,
        "category_info": category_info,
    })

@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    """
    Returns trained ML model telemetry, accuracy, R2 score, and feature importances.
    """
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    return jsonify({"error": "Model metrics not found. Run training first."}), 404

@app.route("/api/historical", methods=["GET"])
def api_historical():
    """
    Provides multi-city summary comparisons and seasonal benchmarks.
    """
    import pandas as pd
    if os.path.exists(HISTORICAL_PATH):
        df = pd.read_csv(HISTORICAL_PATH)
        city_summary = df.groupby("city").agg({
            "aqi": ["mean", "max", "min"],
            "pm25": "mean",
            "pm10": "mean",
            "no2": "mean",
        }).round(1)
        city_summary.columns = ["_".join(c).strip() for c in city_summary.columns.values]
        summary_dict = city_summary.reset_index().to_dict(orient="records")
        return jsonify({"cities": summary_dict, "total_records": len(df)})
    
    # Fallback static benchmarks
    return jsonify({
        "cities": [
            {"city": "Delhi", "aqi_mean": 218.4, "aqi_max": 465, "aqi_min": 65, "pm25_mean": 132.5, "pm10_mean": 218.0},
            {"city": "Panipat", "aqi_mean": 182.6, "aqi_max": 420, "aqi_min": 52, "pm25_mean": 112.0, "pm10_mean": 192.4},
            {"city": "Kolkata", "aqi_mean": 145.2, "aqi_max": 330, "aqi_min": 42, "pm25_mean": 92.0, "pm10_mean": 155.0},
            {"city": "Mumbai", "aqi_mean": 88.5, "aqi_max": 195, "aqi_min": 25, "pm25_mean": 56.4, "pm10_mean": 98.2},
            {"city": "Hyderabad", "aqi_mean": 75.1, "aqi_max": 160, "aqi_min": 22, "pm25_mean": 49.0, "pm10_mean": 86.0},
            {"city": "Bengaluru", "aqi_mean": 48.3, "aqi_max": 115, "aqi_min": 18, "pm25_mean": 38.5, "pm10_mean": 66.1},
        ],
        "total_records": 15000,
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
    print(f"Starting AQI Intelligence & Prediction Dashboard on port {port} ...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

