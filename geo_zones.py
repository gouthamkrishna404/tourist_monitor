# geo_zones.py
from shapely.geometry import Point, Polygon
import os
from supabase import create_client

# ---------------- Supabase setup ----------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_restricted_zones():
    """
    Fetch restricted zones from Supabase.
    Each zone is stored as a list of (lat, lon) tuples in the 'coordinates' JSON column.
    """
    res = supabase.table("restricted_zones").select("*").execute()
    zones = []
    if res.data:
        for row in res.data:
            coords = row.get("coordinates", [])
            if coords:
                zones.append(Polygon([(pt["lat"], pt["lon"]) for pt in coords]))
    return zones

def check_restricted(lat: float, lon: float):
    """
    Check if the given latitude/longitude falls inside any restricted zone.
    Returns a list of alerts if inside a zone.
    """
    point = Point(lat, lon)
    alerts = []
    zones = fetch_restricted_zones()
    for zone in zones:
        if point.within(zone):
            alerts.append("⚠️ Entered restricted area")
    return alerts
