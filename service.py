# service.py
from models import predict_anomaly
from geo_zones import check_restricted

from safe_zone_utils import get_location_info, dwell_time_penalty
from geopy.distance import geodesic
import pandas as pd
import os
from supabase import create_client

# ---------------- Supabase setup ----------------
SUPABASE_URL=https://sggckjpnftehvvqwanei.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ2NranBuZnRlaHZ2cXdhbmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MjcxODcsImV4cCI6MjA3NDQwMzE4N30.OuT0Jpc4J19q700masyC5QQxyNCRdk8Vv1zsiFk_Sqs
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Track previous location for each tourist
prev_locations = {}

def get_user_safe_zones(tourist_id):
    """Fetch user-specific safe zones from Supabase"""
    res = supabase.table("tourist_safe_zones").select("*").eq("tourist_id", tourist_id).execute()
    if res.data:
        return [(row["latitude"], row["longitude"]) for row in res.data], [row["type"] for row in res.data]
    return [], []

def evaluate_tourist(data):
    tourist_id = data.get("tourist_id", "unknown")
    lat = data.get("latitude")
    lon = data.get("longitude")
    timestamp = data.get("timestamp")
    dwell_time = data.get("dwell_time", 0)
    age = data.get("age", 30)
    disabilities = data.get("disabilities", False)
    health_conditions = data.get("health_conditions", False)

    if lat is None or lon is None or timestamp is None:
        return {"error": "Missing latitude, longitude or timestamp"}

    alerts = []
    safety_score = 100
    risk = "Low"

    # --- Compute speed and dwell ---
    prev = prev_locations.get(tourist_id)
    if prev:
        prev_lat, prev_lon, prev_time = prev
        dist = geodesic((prev_lat, prev_lon), (lat, lon)).km
        delta_time = (pd.to_datetime(timestamp) - pd.to_datetime(prev_time)).total_seconds() / 3600
        speed = dist / delta_time if delta_time > 0 else 0
        dwell = delta_time * 60
    else:
        speed = 0
        dwell = dwell_time

    prev_locations[tourist_id] = (lat, lon, timestamp)

    # --- Isolation Forest anomaly ---
    prediction = predict_anomaly(lat, lon, speed, dwell)
    if prediction == -1:
        alerts.append("Anomaly detected")
        safety_score -= 5

    # --- General safe zone check ---
    location_type, min_time, max_time = get_location_info("general", lat, lon)
    penalty = dwell_time_penalty(location_type, dwell, min_time, max_time)
    if penalty > 0:
        alerts.append(f"Dwell time anomaly ({location_type})")
        safety_score -= 5

    # --- User-specific safe zones ---
    user_zones, zone_types = get_user_safe_zones(tourist_id)
    near_fixed_zone = False
    for (zone_lat, zone_lon), zone_type in zip(user_zones, zone_types):
        distance = geodesic((lat, lon), (zone_lat, zone_lon)).meters
        if distance < 50:
            near_fixed_zone = True
            if zone_type in ["hotel", "custom_safe_spot"]:
                loc_type, min_time, max_time = get_location_info(zone_type, zone_lat, zone_lon)
                penalty = dwell_time_penalty(loc_type, dwell, min_time, max_time)
                if penalty > 0:
                    alerts.append(f"Dwell time anomaly ({zone_type})")
                    safety_score -= 10
            break

    # --- Restricted zones ---
    geo_alerts = check_restricted(lat, lon)
    if geo_alerts:
        alerts += geo_alerts
        safety_score -= 20
        risk = "High"

    # --- Speed anomaly ---
    if speed > 50:
        alerts.append("Unusually high speed")
        safety_score -= 10
        if risk != "High":
            risk = "Medium"

    # --- Prolonged dwell ---
    if dwell > 120 and near_fixed_zone:
        alerts.append("Prolonged dwell")
        safety_score -= 5
        if risk != "High":
            risk = "Medium"

    # --- Adjust for elderly/disabled/health conditions ---
    if age >= 60 or disabilities or health_conditions:
        safety_score += 5
        safety_score = min(safety_score, 100)

    safety_score = max(safety_score, 0)

    return {
        "tourist_id": tourist_id,
        "timestamp": timestamp,
        "risk": risk,
        "alerts": alerts,
        "safety_score": safety_score,
        "speed": speed,
        "dwell": dwell
    }
