from fastapi import FastAPI, Request, HTTPException
from supabase import create_client, Client
import os
import math

# ---------------- Supabase setup ----------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sggckjpnftehvvqwanei.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ2NranBuZnRlaHZ2cXdhbmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MjcxODcsImV4cCI6MjA3NDQwMzE4N30.OuT0Jpc4J19q700masyC5QQxyNCRdk8Vv1zsiFk_Sqs"
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ---------------- Helpers ----------------
def haversine_distance(lat1, lon1, lat2, lon2):
    """Compute Haversine distance in km"""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------------- Routes ----------------
@app.post("/evaluate")
async def evaluate_tourist(req: Request):
    try:
        data = await req.json()

        tourist_id = data.get("tourist_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        dwell_time = data.get("dwell_time", 0)
        location_id = data.get("location_id")
        age = data.get("age")
        disabilities = data.get("disabilities")
        health_conditions = data.get("health_conditions")

        # Restricted zones (dummy example)
        restricted_alerts = []
        if latitude and longitude:
            if 43.651 < latitude < 43.652 and -79.348 < longitude < -79.346:
                restricted_alerts.append("⚠️ Entered restricted area")

        # Safe zones (dummy example)
        safe_zones = [{"lat": 43.6515, "lon": -79.347, "type": "hotel"}]

        dwell_alerts = []
        for zone in safe_zones:
            dist = haversine_distance(latitude, longitude, zone["lat"], zone["lon"])
            if dist <= 0.05:  # within 50m
                min_time, max_time = 30, 720
                if dwell_time < min_time or dwell_time > max_time:
                    dwell_alerts.append(
                        f"Dwell time anomaly at {zone['type']} (spent {dwell_time} mins)"
                    )

        # Combine alerts
        combined_alerts = restricted_alerts + dwell_alerts
        combined_message = (
            " | ".join(combined_alerts) if combined_alerts else "SOS triggered by user"
        )

        # Insert into Supabase
        response = supabase.table("alerts").insert(
            {
                "tourist_id": tourist_id,
                "location_id": location_id,
                "alert_type": "Safety Evaluation",
                "message": combined_message,
                "safety_score": 0,
                "status": 2,  # being dealt with
                "sent": 2,    # user-triggered
                "age": age,
                "disabilities": disabilities,
                "health_conditions": health_conditions,
            }
        ).execute()

        if response.get("error"):
            raise HTTPException(status_code=500, detail=response["error"]["message"])

        return {
            "tourist_id": tourist_id,
            "latitude": latitude,
            "longitude": longitude,
            "alerts": combined_alerts,
            "safety_score": 0,
            "risk_level": "Critical",
            "status": 2,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
