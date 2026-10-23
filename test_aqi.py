"""
Comprehensive Automated Test Suite for AQI Prediction & Analytics System.
Verifies breakpoint equations, CPCB/EPA standards, ML inference, and REST API endpoints.
"""

import unittest
import json
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.aqi_calculator import calculate_sub_index, calculate_overall_aqi, get_aqi_category, generate_activity_advice
from src.predictor import predict_aqi
from app import app

class TestAQICalculator(unittest.TestCase):
    """Tests the mathematical sub-index calculations and categories."""

    def test_cpcb_sub_index_pm25_good(self):
        # Breakpoint for 0-30 µg/m3 is 0-50
        val = calculate_sub_index("pm25", 15.0, standard="CPCB")
        self.assertAlmostEqual(val, 25.0, delta=0.5)

    def test_cpcb_sub_index_pm25_moderate(self):
        # Breakpoint for 60.1-90 µg/m3 is 101-200
        val = calculate_sub_index("pm25", 75.0, standard="CPCB")
        self.assertTrue(101 <= val <= 200)

    def test_cpcb_sub_index_pm10(self):
        # Breakpoint for 0-50 µg/m3 is 0-50
        val = calculate_sub_index("pm10", 40.0, standard="CPCB")
        self.assertAlmostEqual(val, 40.0, delta=0.5)

    def test_epa_sub_index_pm25(self):
        # EPA standard: 0 - 12 µg/m3 is 0-50
        val = calculate_sub_index("pm25", 6.0, standard="EPA")
        self.assertAlmostEqual(val, 25.0, delta=1.0)

    def test_dominant_pollutant_identification(self):
        pollutants = {
            "pm25": 120.0,  # sub-index around 300
            "pm10": 45.0,   # sub-index around 45
            "no2": 25.0,    # sub-index around 31
        }
        res = calculate_overall_aqi(pollutants, standard="CPCB")
        self.assertEqual(res["dominant_pollutant"], "PM25")
        self.assertTrue(res["aqi"] >= 300)

    def test_activity_advice_structure(self):
        advice = generate_activity_advice(250, "outdoor cycling", pm25=110, pm10=220)
        self.assertIn("•", advice)
        self.assertTrue(len(advice.split("\n")) >= 2)

class TestMLPredictor(unittest.TestCase):
    """Tests ML inference pipeline."""

    def test_prediction_output_schema(self):
        features = {
            "pm25": 85.0,
            "pm10": 160.0,
            "no2": 45.0,
            "so2": 15.0,
            "co": 1.2,
            "o3": 30.0,
            "nh3": 20.0,
            "temperature": 24.0,
            "humidity": 65.0,
            "wind_speed": 2.8,
            "hour": 14,
            "month": 10,
        }
        res = predict_aqi(features)
        self.assertIn("predicted_aqi", res)
        self.assertIn("predicted_category", res)
        self.assertIn("category_probabilities", res)
        self.assertIn("forecast_24h", res)
        self.assertIsInstance(res["predicted_aqi"], (int, float))
        self.assertTrue(len(res["forecast_24h"]) > 0)

class TestFlaskEndpoints(unittest.TestCase):
    """Tests Flask web server and REST API endpoints."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AeroGuard AI", response.data)

    def test_api_live_endpoint(self):
        response = self.client.get("/api/live?city=Panipat")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("aqi", data)
        self.assertIn("pollutants", data)
        self.assertIn("category_info", data)

    def test_api_predict_endpoint(self):
        payload = {
            "pm25": 55,
            "pm10": 95,
            "no2": 30,
            "temperature": 28,
            "wind_speed": 4.2
        }
        response = self.client.post("/api/predict", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("predicted_aqi", data)
        self.assertIn("predicted_category", data)

    def test_api_calculate_endpoint(self):
        payload = {
            "standard": "CPCB",
            "pollutants": {"pm25": 40, "pm10": 70}
        }
        response = self.client.post("/api/calculate", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("aqi", data)
        self.assertEqual(data["dominant_pollutant"], "PM10")

    def test_api_metrics_endpoint(self):
        response = self.client.get("/api/metrics")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("regression", data)
        self.assertIn("classification", data)
        self.assertIn("feature_importances", data)

    def test_api_historical_endpoint(self):
        response = self.client.get("/api/historical")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("cities", data)

if __name__ == "__main__":
    unittest.main()

