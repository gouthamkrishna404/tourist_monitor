import { serve } from "https://deno.land/std@0.203.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.35.0";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL","https://sggckjpnftehvvqwanei.supabase.co")!;
const SUPABASE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ2NranBuZnRlaHZ2cXdhbmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MjcxODcsImV4cCI6MjA3NDQwMzE4N30.OuT0Jpc4J19q700masyC5QQxyNCRdk8Vv1zsiFk_Sqs")!; // Service key for insert

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), { status: 405 });
  }

  const data = await req.json();

  const {
    tourist_id,
    latitude,
    longitude,
    dwell_time = 0,
    location_id,
    age,
    disabilities,
    health_conditions,
  } = data;

  // Helper to compute haversine distance in km
  const haversineDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371;
    const toRad = (v: number) => (v * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Dummy restricted zones check (replace with your logic)
  const restrictedAlerts: string[] = [];
  if (latitude && longitude) {
    // example: if inside a bounding box
    if (latitude > 43.651 && latitude < 43.652 && longitude > -79.348 && longitude < -79.346) {
      restrictedAlerts.push("Entered restricted area");
    }
  }

  // Dummy safe zones (replace with DB fetch)
  const safeZones: Array<{ lat: number; lon: number; type: string }> = [
    { lat: 43.6515, lon: -79.347, type: "hotel" },
  ];

  const dwellAlerts: string[] = [];
  for (const zone of safeZones) {
    const dist = haversineDistance(latitude, longitude, zone.lat, zone.lon);
    if (dist <= 0.05) {
      const minTime = 30;
      const maxTime = 720;
      if (dwell_time < minTime || dwell_time > maxTime) {
        dwellAlerts.push(`⚠️ Dwell time anomaly at ${zone.type} (spent ${dwell_time} mins)`);
      }
    }
  }

  const combinedAlerts = [...restrictedAlerts, ...dwellAlerts];
  const combinedMessage = combinedAlerts.length
    ? combinedAlerts.join(" | ")
    : "⚠️ SOS triggered by user";

  // Insert alert into Supabase
  const { error } = await supabase.from("alerts").insert({
    tourist_id,
    location_id,
    alert_type: "Safety Evaluation",
    message: combinedMessage,
    safety_score: 0,
    status: 2, // being dealt with
    sent: 2,   // user-triggered
    age,
    disabilities,
    health_conditions,
  });

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }

  return new Response(
    JSON.stringify({
      tourist_id,
      latitude,
      longitude,
      alerts: combinedAlerts,
      safety_score: 0,
      risk_level: "Critical",
      status: 2,
    }),
    { headers: { "Content-Type": "application/json" } }
  );
});
