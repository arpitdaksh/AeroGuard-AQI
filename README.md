# AeroGuard AI — Air Quality Index (AQI) Intelligence & Machine Learning Suite

An end-to-end environmental machine learning, analytics, and interactive web dashboard system. It provides real-time AQI tracking, standard Central Pollution Control Board (CPCB India) and US EPA breakpoint interpolation, dual Random Forest predictive models, live global city lookup via Open-Meteo, and personalized AI health & fitness recommendations.

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
   - **AQI Regressor** (`RandomForestRegressor`): Predicts continuous numerical AQI with $R^2 > 0.99$ based on atmospheric pollutants and meteorological parameters (Temperature, Humidity, Wind Speed, Pressure, Hour, Month).
   - **AQI Classifier** (`RandomForestClassifier`): Predicts discrete environmental danger categories with $>99\%$ validation accuracy and outputs real-time probability distributions across all risk buckets.
   - **24-Hour Diurnal ML Simulation**: Simulates future rush-hour spikes, nighttime thermal inversion, and afternoon wind dispersion.

3. **Live Global Air Quality Sensor Integration**:
   - Free, zero-API-key integration with the **Open-Meteo Air Quality and Geocoding APIs**.
   - Real-time weather and pollution lookup for any city worldwide (e.g. Panipat, Delhi, Mumbai, Bengaluru, London, New York, Tokyo).
   - Intelligent offline fallback simulation for air-gapped or network-restricted environments.

4. **AeroGuard AI Health & Fitness Advisor**:
   - Activity-specific risk analysis tailored to the user's planned workout (e.g., "outdoor running", "weight training", "morning walk", "cycling", "HIIT").
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
- $C_p$: Actual monitored concentration of pollutant $p$
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
│   ├── aqi_regressor.joblib            # Trained Random Forest Regressor
│   ├── aqi_classifier.joblib           # Trained Random Forest Classifier
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
└── README.md                          # Documentation and user guide
```

---

## 🚀 Getting Started

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
python --version
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Retrain Models (Optional)
The pre-trained models are already saved in `models/`. To retrain:
```bash
python src/train.py
```

### 4. Run Automated Test Suite
```bash
python test_aqi.py
```

### 5. Launch Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Interactive Web Dashboard |
| `/api/live?city={name}&standard={CPCB\|EPA}` | `GET` | Real-time global atmospheric air quality & weather |
| `/api/predict` | `POST` | ML Regressor & Classifier inference from custom inputs |
| `/api/calculate` | `POST` | Deterministic regulatory standard calculation |
| `/api/advice` | `POST` | AI activity & workout health recommendation |
| `/api/metrics` | `GET` | Machine learning model training performance & feature importances |
| `/api/historical` | `GET` | Multi-city historical benchmarks and seasonality data |

