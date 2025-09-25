# safe_zone_utils.py
from supabase import create_client
import os

# ---------------- Supabase setup ----------------
SUPABASE_URL = os.environ.get("https://sggckjpnftehvvqwanei.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ2NranBuZnRlaHZ2cXdhbmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MjcxODcsImV4cCI6MjA3NDQwMzE4N30.OuT0Jpc4J19q700masyC5QQxyNCRdk8Vv1zsiFk_Sqs")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Example location info metadata
LOCATION_INFO = {
    "general": {"min_time": 5, "max_time": 60},  # in minutes
    "hotel": {"min_time": 30, "max_time": 720},
    "custom_safe_spot": {"min_time": 10, "max_time": 180}
}

def get_location_info(location_type: str, lat=None, lon=None):
    """
    Fetch location info for dwell time checks.
    Optionally, you can extend this to fetch dynamic info from Supabase.
    """
    info = LOCATION_INFO.get(location_type, {"min_time": 5, "max_time": 60})
    return location_type, info["min_time"], info["max_time"]

def dwell_time_penalty(location_type: str, dwell_time: float, min_time: float, max_time: float) -> int:
    """
    Compute penalty based on dwell time at a location.
    Returns 0 if within limits, otherwise >0 if anomaly.
    """
    if dwell_time < min_time or dwell_time > max_time:
        return 1
    return 0

def get_user_safe_zones(tourist_id: str):
    """
    Fetch user-specific safe zones from Supabase.
    Returns list of (lat, lon) and their type.
    """
    res = supabase.table("tourist_safe_zones").select("*").eq("tourist_id", tourist_id).execute()
    if res.data:
        zones = [(row["latitude"], row["longitude"]) for row in res.data]
        types = [row["type"] for row in res.data]
        return zones, types
    return [], []
