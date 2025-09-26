from supabase import create_client
import os
from typing import List, Tuple

# ---------------- Supabase setup ----------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sggckjpnftehvvqwanei.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ2NranBuZnRlaHZ2cXdhbmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MjcxODcsImV4cCI6MjA3NDQwMzE4N30.OuT0Jpc4J19q700masyC5QQxyNCRdk8Vv1zsiFk_Sqs"
)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Static location info
LOCATION_INFO = {
    "general": {"min_time": 5, "max_time": 60},
    "hotel": {"min_time": 30, "max_time": 720},
    "custom_safe_spot": {"min_time": 10, "max_time": 180}
}

def get_location_info(location_type: str) -> Tuple[int, int]:
    """Return min and max dwell time for a given location type."""
    info = LOCATION_INFO.get(location_type, {"min_time": 5, "max_time": 60})
    return info["min_time"], info["max_time"]

def dwell_time_penalty(dwell_time: float, min_time: float, max_time: float) -> int:
    """Return 0 if dwell_time is within limits, 1 if outside."""
    return 0 if min_time <= dwell_time <= max_time else 1

def get_user_safe_zones(tourist_id: str) -> List[Tuple[float, float, str]]:
    """Fetch safe zones for a tourist from Supabase."""
    res = supabase.table("tourist_safe_zones").select("*").eq("tourist_id", tourist_id).execute()
    if res.data:
        return [(row["latitude"], row["longitude"], row["type"]) for row in res.data]
    return []
