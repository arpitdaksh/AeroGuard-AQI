"""
Synthetic & Historical Atmospheric Data Generator.
Generates realistic multi-city time-series environmental data capturing diurnal cycles,
seasonal variations (winter inversion, monsoon washout), and weather correlations.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

CITIES = {
    "Panipat": {"lat": 29.3909, "lon": 76.9635, "base_pm25": 110, "base_pm10": 190, "industrial_factor": 1.3},
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "base_pm25": 125, "base_pm10": 210, "industrial_factor": 1.4},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "base_pm25": 55, "base_pm10": 95, "industrial_factor": 0.8},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "base_pm25": 38, "base_pm10": 65, "industrial_factor": 0.6},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "base_pm25": 90, "base_pm10": 150, "industrial_factor": 1.1},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "base_pm25": 48, "base_pm10": 85, "industrial_factor": 0.7},
}

def generate_city_dataset(days: int = 180, output_path: str = "data/city_aqi_historical.csv") -> pd.DataFrame:
    """
    Generates hourly environmental readings across multiple cities for the specified number of days.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    hours_total = days * 24

    records = []

    for city_name, meta in CITIES.items():
        base_pm25 = meta["base_pm25"]
        base_pm10 = meta["base_pm10"]
        ind_factor = meta["industrial_factor"]

        # Time series generation
        time_index = [start_date + timedelta(hours=i) for i in range(hours_total)]

        for t in time_index:
            hour = t.hour
            month = t.month
            day_of_week = t.weekday()

            # Diurnal rush-hour effects (8-10 AM, 6-9 PM)
            traffic_rush = 1.4 if (8 <= hour <= 10 or 18 <= hour <= 21) else (0.8 if 1 <= hour <= 5 else 1.0)
            if day_of_week in [5, 6]:
                traffic_rush *= 0.85  # Weekend reduction

            # Seasonal factors: Winter (Nov-Jan) has thermal inversion; Monsoon (Jul-Aug) has rain cleansing
            if month in [11, 12, 1]:  # Winter inversion
                season_mult = 1.85
                temp_base = 14.0 + 8.0 * np.sin((hour - 8) * np.pi / 12)
                humidity_base = 75.0 + 15.0 * np.cos(hour * np.pi / 12)
                wind_speed_base = np.random.uniform(1.0, 3.5)
                rainfall = 0.0
            elif month in [6, 7, 8, 9]:  # Monsoon
                season_mult = 0.55
                temp_base = 28.0 + 6.0 * np.sin((hour - 8) * np.pi / 12)
                humidity_base = 85.0 + 10.0 * np.sin(hour * np.pi / 12)
                wind_speed_base = np.random.uniform(4.0, 8.5)
                rainfall = np.random.choice([0.0, 5.0, 15.0, 35.0], p=[0.6, 0.2, 0.15, 0.05])
            else:  # Spring / Summer / Autumn
                season_mult = 1.05
                temp_base = 32.0 + 9.0 * np.sin((hour - 8) * np.pi / 12)
                humidity_base = 45.0 + 15.0 * np.cos(hour * np.pi / 12)
                wind_speed_base = np.random.uniform(2.5, 6.0)
                rainfall = 0.0

            # Wind cleansing effect (higher wind speed disperses particulate matter)
            wind_dispersion = max(0.4, 1.0 - (wind_speed_base - 2.0) * 0.08)

            # Rain washout effect
            rain_washout = 0.35 if rainfall > 10 else (0.7 if rainfall > 0 else 1.0)

            # Noise components
            noise_pm25 = np.random.normal(0, 8)
            noise_pm10 = np.random.normal(0, 15)

            # Calculate pollutants
            pm25 = max(5.0, (base_pm25 * season_mult * traffic_rush * wind_dispersion * rain_washout * ind_factor) + noise_pm25)
            pm10 = max(pm25 * 1.3, (base_pm10 * season_mult * traffic_rush * wind_dispersion * rain_washout * ind_factor) + noise_pm10)
            
            # NO2 strongly correlated with traffic rush & vehicles
            no2 = max(5.0, (35.0 * traffic_rush * ind_factor * season_mult * wind_dispersion) + np.random.normal(0, 5))
            
            # SO2 industrial emissions
            so2 = max(3.0, (18.0 * ind_factor * season_mult * wind_dispersion) + np.random.normal(0, 3))
            
            # CO traffic & combustion (mg/m3)
            co = max(0.2, (1.2 * traffic_rush * ind_factor * season_mult) + np.random.normal(0, 0.2))
            
            # Ozone (O3) photochemical reaction: peaks in sunny afternoon hours with high temp & solar radiation
            solar_factor = max(0.0, np.sin((hour - 6) * np.pi / 12)) if 6 <= hour <= 18 else 0.0
            o3 = max(5.0, (30.0 + 55.0 * solar_factor * (temp_base / 30.0)) + np.random.normal(0, 6))

            # Ammonia (NH3)
            nh3 = max(5.0, (25.0 * ind_factor * season_mult) + np.random.normal(0, 4))

            # Atmospheric Pressure (hPa)
            pressure = 1013.25 - (temp_base * 0.15) + np.random.normal(0, 1.5)

            records.append({
                "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                "city": city_name,
                "hour": hour,
                "month": month,
                "day_of_week": day_of_week,
                "pm25": round(pm25, 2),
                "pm10": round(pm10, 2),
                "no2": round(no2, 2),
                "so2": round(so2, 2),
                "co": round(co, 3),
                "o3": round(o3, 2),
                "nh3": round(nh3, 2),
                "temperature": round(temp_base, 1),
                "humidity": round(humidity_base, 1),
                "wind_speed": round(wind_speed_base, 2),
                "rainfall": round(rainfall, 1),
                "pressure": round(pressure, 1),
            })

    df = pd.DataFrame(records)

    # Compute actual CPCB calculated AQI for training target
    try:
        from src.aqi_calculator import calculate_overall_aqi, get_aqi_category
    except ImportError:
        from aqi_calculator import calculate_overall_aqi, get_aqi_category

    aqi_values = []
    aqi_categories = []

    for _, row in df.iterrows():
        p_dict = {
            "pm25": row["pm25"],
            "pm10": row["pm10"],
            "no2": row["no2"],
            "so2": row["so2"],
            "co": row["co"],
            "o3": row["o3"],
            "nh3": row["nh3"],
        }
        res = calculate_overall_aqi(p_dict, standard="CPCB")
        aqi_values.append(res["aqi"])
        aqi_categories.append(res["category_info"]["category"])

    df["aqi"] = aqi_values
    df["aqi_category"] = aqi_categories

    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} atmospheric records across {len(CITIES)} cities into {output_path}")
    return df

if __name__ == "__main__":
    generate_city_dataset(days=90)
