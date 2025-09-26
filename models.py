import os
import joblib
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.pkl")

# Load model and scaler once at startup
model, scaler = joblib.load(MODEL_PATH)


def predict_anomaly(lat, lon, speed=0, dwell=0):
    """
    Predict if a location is anomalous.
    Returns: 1 = normal, -1 = anomaly
    """
    X_scaled = scaler.transform([[lat, lon, speed, dwell]])
    return model.predict(X_scaled)[0]


# Example usage:
if __name__ == "__main__":
    result = predict_anomaly(43.65107, -79.347015, speed=5, dwell=10)
    print("Anomaly prediction:", result)
