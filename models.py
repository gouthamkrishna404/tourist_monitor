import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from geopy.distance import geodesic

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "locations.csv")
MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.pkl")


def compute_features(df):
    """
    Compute speed (km/h) and dwell time (minutes) for each tourist's locations.
    """
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
            delta_time = (time - prev_time).total_seconds() / 3600  # hours

            speed = dist / delta_time if delta_time > 0 else 0  # km/h
            dwell = delta_time * 60  # minutes

            speeds.append(speed)
            dwells.append(dwell)

        prev_lat, prev_lon, prev_time = lat, lon, time

    df["speed"] = speeds
    df["dwell"] = dwells
    return df


def train_model():
    """
    Train Isolation Forest anomaly detection model and save it with scaler.
    """
    if not os.path.exists(CSV_PATH):
        print("❌ No locations.csv found to train model.")
        return

    df = pd.read_csv(CSV_PATH)
    df = compute_features(df)

    X = df[["latitude", "longitude", "speed", "dwell"]]

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_scaled)

    # Save both model and scaler
    joblib.dump((model, scaler), MODEL_PATH)
    print("✅ Isolation Forest model trained and saved.")


def predict_anomaly(lat, lon, speed=0, dwell=0):
    """
    Predict if a location is anomalous.
    Returns: 1 = normal, -1 = anomaly
    """
    if not os.path.exists(MODEL_PATH):
        train_model()

    model, scaler = joblib.load(MODEL_PATH)

    X_test_scaled = scaler.transform([[lat, lon, speed, dwell]])
    return model.predict(X_test_scaled)[0]


# Example usage:
if __name__ == "__main__":
    # Optionally train model first
    train_model()

    # Predict anomaly for a new location
    result = predict_anomaly(43.65107, -79.347015, speed=5, dwell=10)
    print("Anomaly prediction:", result)
