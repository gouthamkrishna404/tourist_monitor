from shapely.geometry import Point, Polygon
import os
from supabase import create_client

# ---------------- Supabase setup ----------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sggckjpnftehvvqwanei.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ2NranBuZnRlaHZ2cXdhbmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MjcxODcsImV4cCI6MjA3NDQwMzE4N30.OuT0Jpc4J19q700masyC5QQxyNCRdk8Vv1zsiFk_Sqs"
)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_restricted_zones():
    """
    Fetch restricted zones from Supabase.
    Each zone is stored as a list of {lat, lon} in 'coordinates' JSON column.
    Returns list of Shapely Polygons.
    """
    res = supabase.table("restricted_zones").select("coordinates").execute()
    zones = []
    if res.data:
        for row in res.data:
            coords = row.get("coordinates", [])
            if coords:
                # Convert [{lat, lon}, ...] → [(lon, lat), ...] for Shapely
                polygon_points = [(pt["lon"], pt["lat"]) for pt in coords]
                zones.append(Polygon(polygon_points))
    return zones


def check_restricted(lat: float, lon: float):
    """
    Check if the given latitude/longitude falls inside any restricted zone.
    Returns a list of alerts if inside a zone.
    """
    point = Point(lon, lat)  # IMPORTANT: (x=lon, y=lat)
    alerts = []
    zones = fetch_restricted_zones()
    for zone in zones:
        if zone.is_valid and point.within(zone):
            alerts.append("⚠️ Entered restricted area")
    return alerts
