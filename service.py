# service.py
from geo_zones import check_restricted
from safe_zone_utils import get_user_safe_zones, get_location_info, dwell_time_penalty
from shapely.geometry import Point
import math

def evaluate_tourist(data: dict):
    """
    Main logic to evaluate tourist risk.
    Returns structured dict with risk, alerts, and safety score.
    """
    tourist_id = data.get("tourist_id")
    lat = data.get("latitude")
    lon = data.get("longitude")
    dwell_time = data.get("dwell_time", 0)

    alerts = []

    # 1️⃣ Check restricted zones
    alerts.extend(check_restricted(lat, lon))

    # 2️⃣ Check dwell time against safe zones
    safe_zones = get_user_safe_zones(tourist_id)
    for zone_lat, zone_lon, zone_type in safe_zones:
        distance = haversine_distance(lat, lon, zone_lat, zone_lon)
        # Consider within 50 meters as being in that safe zone
        if distance <= 0.05:
            min_time, max_time = get_location_info(zone_type)
            penalty = dwell_time_penalty(dwell_time, min_time, max_time)
            if penalty:
                alerts.append(f"⚠️ Dwell time anomaly at {zone_type}")
    
    # 3️⃣ Compute safety score
    safety_score = max(0, 100 - len(alerts) * 25)  # example scoring
    risk_level = "Low" if safety_score > 75 else "Medium" if safety_score > 50 else "High"

    return {
        "tourist_id": tourist_id,
        "latitude": lat,
        "longitude": lon,
        "alerts": alerts,
        "safety_score": safety_score,
        "risk_level": risk_level
    }


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns distance in km between two coordinates
    """
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
