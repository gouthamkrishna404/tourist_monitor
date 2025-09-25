import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from geopy.distance import geodesic

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "locations.csv")
MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.pkl")

def compute_features(df):
    df = df.sort_values(["tourist_id", "timestamp"])
    speeds, dwells = [], []
    prev_lat = prev_lon = prev_time = None
    for _, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        time = pd.to_datetime(row["timestamp"])
        if prev_lat is None:
            speeds.append(0)
            dwells.append(0)
        else:
            dist = geodesic((prev_lat, prev_lon), (lat, lon)).km
            delta_time = (time - prev_time).total_seconds() / 3600
            speeds.append(dist / delta_time if delta_time > 0 else 0)
            dwells.append(delta_time * 60)
        prev_lat, prev_lon, prev_time = lat, lon, time

    df["speed"] = speeds
    df["dwell"] = dwells
    return df

def train_model():
    if not os.path.exists(CSV_PATH):
        print("No locations.csv found to train model.")
        return
    df = pd.read_csv(CSV_PATH)
    df = compute_features(df)
    X = df[["latitude","longitude","speed","dwell"]]
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    print("✅ Isolation Forest model trained.")

def predict_anomaly(lat, lon, speed=0, dwell=0):
    if not os.path.exists(MODEL_PATH):
        train_model()
    model = joblib.load(MODEL_PATH)
    return model.predict([[lat, lon, speed, dwell]])[0]  # 1=normal, -1=anomaly
