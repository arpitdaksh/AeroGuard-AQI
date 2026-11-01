# 🌬️ AeroGuard AI — Air Quality Index (AQI) Intelligence & Machine Learning Suite

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask_3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![TailwindCSS](https://img.shields.io/badge/UI-TailwindCSS-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Render Deploy](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render&logoColor=white)](https://render.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end environmental Machine Learning, analytics, and interactive web dashboard system. It provides real-time AQI tracking, standard Central Pollution Control Board (CPCB India) and US EPA breakpoint interpolation, dual Random Forest predictive models, live global city lookup via Open-Meteo, and personalized AI health & fitness recommendations.

> **Project description:** AeroGuard AI is a Flask-based air quality intelligence platform that combines CPCB and US EPA AQI calculations, machine learning forecasts, live Open-Meteo data, interactive analytics, and personalized health guidance in one dashboard.

---

## 🌐 Live Demo & Deployment

| Platform | Deployment Status | Link |
|---|---|---|
| **Render Cloud (Live Web App)** | ![Status](https://img.shields.io/badge/Status-Live-emerald) | [https://aeroguard-aqi-app.onrender.com](https://aeroguard-aqi-app.onrender.com) |
| **Local Dashboard** | ![Local](https://img.shields.io/badge/Local-127.0.0.1%3A5000-blue) | [http://127.0.0.1:5000](http://127.0.0.1:5000) |

> **Deploy to Render in 1-Click:**
> [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## 🌟 Key Features

1. **Dual Standard AQI Mathematical Engine (CPCB & US EPA)**:
   - Piecewise linear interpolation sub-index calculations for:
     - $\text{PM}_{2.5}$ (Fine inhalable particulate matter)
     - $\text{PM}_{10}$ (Coarse dust matter)
     - $\text{NO}_2$ (Nitrogen dioxide — vehicular traffic marker)
     - $\text{SO}_2$ (Sulfur dioxide — industrial coal & power plant emissions)
     - $\text{CO}$ (Carbon monoxide — incomplete combustion)
     - $\text{O}_3$ (Ground-level ozone — photochemical reaction)
     - $\text{NH}_3$ (Ammonia — agricultural & chemical emissions)
   - Dynamic identification of the **Dominant Critical Pollutant**.

2. **Machine Learning Predictive Models**:
   - **AQI Regressor** (`RandomForestRegressor`): Predicts continuous numerical AQI with $R^2 = 0.9991$ based on atmospheric pollutants and meteorological parameters (Temperature, Humidity, Wind Speed, Pressure, Hour, Month).
   - **AQI Classifier** (`RandomForestClassifier`): Predicts discrete environmental danger categories with $99.77\%$ validation accuracy and outputs real-time probability distributions across all risk buckets.
   - **24-Hour Diurnal ML Simulation**: Simulates future rush-hour spikes, nighttime thermal inversion, and afternoon wind dispersion.

3. **Live Global Air Quality Sensor Integration**:
   - Free, zero-API-key integration with the **Open-Meteo Air Quality and Geocoding APIs**.
   - Real-time weather and pollution lookup for any city worldwide (e.g. Panipat, Delhi, Mumbai, Bengaluru, London, New York, Tokyo).
   - Intelligent offline fallback simulation for air-gapped or network-restricted environments.

4. **AeroGuard AI Health & Fitness Advisor**:
   - Activity-specific risk analysis tailored to the user's planned workout (e.g., *"outdoor running"*, *"weight training"*, *"morning walk"*, *"cycling"*, *"HIIT"*).
   - Explicit N95/N99 respirator alerts based on PM2.5 thresholds.
   - Suggestions on workout timing and ventilation controls.

5. **Interactive "What-If" Environmental Policy Simulator**:
   - Real-time interactive sliders allowing users to simulate emission reduction scenarios (e.g. 30% reduction in vehicular $\text{NO}_2$, dust suppression for $\text{PM}_{10}$, or wind speed variation).
   - Real-time comparison between Machine Learning predictions and official regulatory formula calculations.

6. **Interactive Analytics & Visualizations**:
   - Dynamic SVG circular radial gauge with status glow and animations.
   - 24-hour diurnal trend line chart.
   - Pollutant radar fingerprint chart.
   - Multi-city historical benchmark bar charts (winter peaks vs. monsoons).
   - Machine learning feature importance rankings.
   - One-click JSON assessment report download.

---

## 📐 Mathematical Formulation

The standard breakpoint linear interpolation sub-index $I_p$ for pollutant concentration $C_p$ is calculated as:

$$I_p = \frac{I_{Hi} - I_{Lo}}{BP_{Hi} - BP_{Lo}} \times (C_p - BP_{Lo}) + I_{Lo}$$

Where:
- $I_p$: Sub-index for pollutant $p$
- $C_p$: Monitored concentration of pollutant $p$
- $BP_{Hi}, BP_{Lo}$: Breakpoint concentrations enclosing $C_p$
- $I_{Hi}, I_{Lo}$: Sub-index values corresponding to $BP_{Hi}$ and $BP_{Lo}$

The overall Air Quality Index is determined by the maximum sub-index:

$$\text{AQI} = \max(I_{\text{PM2.5}}, I_{\text{PM10}}, I_{\text{NO2}}, I_{\text{SO2}}, I_{\text{CO}}, I_{\text{O3}}, I_{\text{NH3}})$$

---

## 🗂️ Project Directory Structure

```
AQI Project/
│
├── data/
│   └── city_aqi_historical.csv         # 17,280 hourly multi-city atmospheric records
│
├── models/
│   ├── aqi_regressor.joblib            # Trained Random Forest Regressor (R² = 0.9991)
│   ├── aqi_classifier.joblib           # Trained Random Forest Classifier (Accuracy = 99.77%)
│   └── metrics.json                    # Model telemetry & feature importances
│
├── src/
│   ├── __init__.py
│   ├── aqi_calculator.py              # CPCB & US EPA breakpoint interpolation engine
│   ├── data_generator.py              # Multi-city seasonal & diurnal atmospheric generator
│   ├── live_api.py                    # Real-time Open-Meteo API integration with fallback
│   ├── predictor.py                   # High-performance ML inference engine
│   └── train.py                       # Scikit-learn model training & evaluation pipeline
│
├── static/
│   ├── css/
│   │   └── style.css                  # Custom animations, sliders, and glassmorphism styling
│   └── js/
│       └── app.js                     # Chart.js visualizations, state management & REST calls
│
├── templates/
│   └── index.html                     # Responsive web dashboard
│
├── app.py                             # Flask web application & REST API server
├── test_aqi.py                        # Automated unit & integration test suite (13 tests)
├── requirements.txt                   # Project Python dependencies
├── Procfile                           # Production Gunicorn process file
├── render.yaml                        # 1-Click Render Cloud deployment blueprint
└── README.md                          # Documentation and user guide
```

---

## 📦 System Requirements & Dependencies

### Python Environment
- Python 3.10, 3.11 or 3.12
- Operating System: Windows, macOS, or Linux

### Key Packages
```text
flask>=3.0.0
flask-cors>=4.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
joblib>=1.3.0
requests>=2.31.0
python-dotenv>=1.0.0
gunicorn>=21.0.0
```

---

## 🚀 Local Setup & Installation

### 1. Clone or Open Project
```bash
git clone https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
cd "AQI Project"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python test_aqi.py
```
*(All 13 unit tests will verify breakpoint mathematics, ML pipeline, and endpoints).*

### 4. Launch Application
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## ☁️ Free Cloud Deployment Guide (Render)

This repository includes both `Procfile` and `render.yaml` for zero-configuration cloud deployment:

1. **Push your code to GitHub** (see instructions below).
2. Sign in to **[Render.com](https://render.com/)** with your GitHub account.
3. Click **New +** -> **Web Service**.
4. Select your GitHub repository.
5. Render will auto-detect settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --workers 2 --threads 2 --timeout 60`
6. Click **Deploy Web Service**.
7. In ~2 minutes, your live web app URL will be available!

---

## 📡 REST API Reference

| Endpoint | Method | Parameters | Description |
|---|---|---|---|
| `/` | `GET` | None | Interactive UI Web Dashboard |
| `/api/live` | `GET` | `city`, `standard`, `activity` | Real-time global atmospheric air quality & weather |
| `/api/predict` | `POST` | JSON (Pollutants & Weather) | ML Regressor & Classifier inference + 24h forecast |
| `/api/calculate` | `POST` | JSON (Pollutants, Standard) | Deterministic regulatory standard calculation |
| `/api/advice` | `POST` | JSON (AQI, Activity, PM levels) | AI activity & workout health recommendation |
| `/api/metrics` | `GET` | None | Machine learning model training performance & feature importances |
| `/api/historical` | `GET` | None | Multi-city historical benchmarks and seasonality data |
