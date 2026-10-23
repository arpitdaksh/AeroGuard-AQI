"""
Machine Learning Training Pipeline.
Trains Random Forest Regressor and Classifier on multi-city environmental time-series data.
Saves models to `models/` and evaluation metrics to `models/metrics.json`.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
try:
    from src.data_generator import generate_city_dataset
except ImportError:
    from data_generator import generate_city_dataset

FEATURE_COLUMNS = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3",
    "nh3",
    "temperature",
    "humidity",
    "wind_speed",
    "rainfall",
    "pressure",
    "hour",
    "month",
]

def train_models(dataset_path: str = "data/city_aqi_historical.csv", model_dir: str = "models/"):
    """
    Trains and saves ML models and performance telemetry.
    """
    os.makedirs(model_dir, exist_ok=True)

    # 1. Load or Generate Dataset
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}, generating realistic dataset...")
        df = generate_city_dataset(days=120, output_path=dataset_path)
    else:
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)

    print(f"Dataset shape: {df.shape}")

    X = df[FEATURE_COLUMNS]
    y_reg = df["aqi"]
    y_clf = df["aqi_category"]

    # 2. Train-Test Split
    X_train, X_test, y_reg_train, y_reg_test = train_test_split(
        X, y_reg, test_size=0.2, random_state=42
    )
    _, _, y_clf_train, y_clf_test = train_test_split(
        X, y_clf, test_size=0.2, random_state=42
    )

    # 3. Train Regression Model (Random Forest Regressor)
    print("Training Random Forest Regressor...")
    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=16,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    regressor.fit(X_train, y_reg_train)

    y_reg_pred = regressor.predict(X_test)
    r2 = float(r2_score(y_reg_test, y_reg_pred))
    mae = float(mean_absolute_error(y_reg_test, y_reg_pred))
    rmse = float(np.sqrt(mean_squared_error(y_reg_test, y_reg_pred)))

    print(f"Regressor Performance -> R²: {r2:.4f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}")

    # 4. Train Classification Model (Random Forest Classifier)
    print("Training Random Forest Classifier...")
    classifier = RandomForestClassifier(
        n_estimators=100,
        max_depth=16,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    classifier.fit(X_train, y_clf_train)

    y_clf_pred = classifier.predict(X_test)
    acc = float(accuracy_score(y_clf_test, y_clf_pred))
    clf_classes = list(classifier.classes_)
    cm = confusion_matrix(y_clf_test, y_clf_pred, labels=clf_classes).tolist()
    report = classification_report(y_clf_test, y_clf_pred, output_dict=True)

    print(f"Classifier Performance -> Accuracy: {acc * 100:.2f}%")

    # 5. Extract Feature Importances
    feature_importances = {
        col: round(float(imp), 4)
        for col, imp in zip(FEATURE_COLUMNS, regressor.feature_importances_)
    }
    sorted_importances = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)

    # 6. Save Models
    regressor_path = os.path.join(model_dir, "aqi_regressor.joblib")
    classifier_path = os.path.join(model_dir, "aqi_classifier.joblib")

    joblib.dump(regressor, regressor_path)
    joblib.dump(classifier, classifier_path)
    print(f"Saved models to {regressor_path} and {classifier_path}")

    # 7. Save Metrics Telemetry
    metrics = {
        "dataset_rows": len(df),
        "features": FEATURE_COLUMNS,
        "regression": {
            "model": "Random Forest Regressor (100 estimators, depth=16)",
            "r2_score": round(r2, 4),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
        },
        "classification": {
            "model": "Random Forest Classifier (100 estimators, depth=16)",
            "accuracy": round(acc, 4),
            "classes": clf_classes,
            "confusion_matrix": cm,
            "detailed_report": report,
        },
        "feature_importances": dict(sorted_importances),
    }

    metrics_path = os.path.join(model_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved evaluation metrics to {metrics_path}")

    return metrics

if __name__ == "__main__":
    train_models()
