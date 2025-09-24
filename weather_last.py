import requests
from supabase import create_client, Client
from datetime import datetime, timezone

print("=== Getting Weather Data for Last Coordinate ===")

# Supabase and API details
SUPABASE_URL = "https://cjdnywouhyxugcpoolim.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqZG55d291aHl4dWdjcG9vbGltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODMwNDgzNCwiZXhwIjoyMDczODgwODM0fQ.E1YocS4a1XF34_oEz6Q6cz9zU-V5W6Y99z4vyKNqLRk"
API_KEY = "632bf45cfb44fbae29203ecce7feea50"

try:
    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
    print("✅ Connected to Supabase")
    
    # Get the LAST row from coordinates
    coords_data = supabase.table("coordinates").select("*").order("id", desc=True).limit(1).execute()
    coords_list = coords_data.data

    if not coords_list:
        print("❌ No coordinates found")
        exit()
        
    coord = coords_list[0]  # Only the last row

    # Grab details
    lat = coord["latitude"]
    lon = coord["longitude"]
    place_name = coord.get("place_name", "")
    city = coord.get("city", "")
    coord_id = coord["id"]
    device_id = coord.get("device_id", "SENSOR001")
    device_secret = coord.get("device_secret", "q8t7r6y5u4i3o2p1a0s9d8f7g6h5j4k3")

    print(f"📍 Last coordinate: {place_name}, {city} (lat {lat}, lon {lon})")

    # Get weather data
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        weather_data = response.json()
        record = {
            "coord_id": coord_id,
            "device_id": device_id,
            "device_secret": device_secret,
            "place_name": place_name,
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "weather_description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("weather_by_coords").insert(record).execute()
        print(f"✅ Weather data saved for {place_name}, {city}")
    else:
        print(f"❌ Failed to get weather for {place_name}")

except Exception as e:
    print(f"❌ Critical error: {e}")

print("=== Done! ===")
