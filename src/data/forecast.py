import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# National Weather Service API for Chicago O'Hare
URL = "https://api.weather.gov/gridpoints/LOT/66,77"

headers = {
    "User-Agent": "coms5730-class-project (student academic project)",
    "Accept": "application/geo+json"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()
rainfall = data["properties"]["quantitativePrecipitation"]

# Store daily rainfall totals
daily_rainfall = {}

chicago_time = ZoneInfo("America/Chicago")

for period in rainfall["values"]:

    if period["value"] is None:
        continue

    # Example: 2026-11-04T06:00:00+00:00/PT6H
    start_text, duration_text = period["validTime"].split("/")

    start_time = datetime.fromisoformat(start_text)
    hours = int(duration_text.replace("PT", "").replace("H", ""))

    end_time = start_time + timedelta(hours=hours)

    # Convert forecast period into Chicago time
    start_local = start_time.astimezone(chicago_time)
    end_local = end_time.astimezone(chicago_time)

    # Convert millimeters to inches
    rain_inches = period["value"] / 25.4

    # Split periods that cross midnight
    current_time = start_local

    while current_time < end_local:

        next_midnight = datetime.combine(
            current_time.date() + timedelta(days=1),
            datetime.min.time(),
            tzinfo=chicago_time
        )

        segment_end = min(next_midnight, end_local)

        segment_hours = (
            segment_end.astimezone(ZoneInfo("UTC"))
            - current_time.astimezone(ZoneInfo("UTC"))
        ).total_seconds() / 3600

        total_hours = (
            end_local.astimezone(ZoneInfo("UTC"))
            - start_local.astimezone(ZoneInfo("UTC"))
        ).total_seconds() / 3600

        segment_rain = rain_inches * segment_hours / total_hours

        day = current_time.date().isoformat()

        if day not in daily_rainfall:
            daily_rainfall[day] = 0

        daily_rainfall[day] += segment_rain

        current_time = segment_end

print("NWS Daily Rainfall Forecast (Chicago)")
print("-------------------------------------")

today = datetime.now(chicago_time).date()

for day in sorted(daily_rainfall):
    forecast_date = datetime.fromisoformat(day).date()

    if today <= forecast_date < today + timedelta(days=3):
        print(day, ":", round(daily_rainfall[day], 3), "inches")
    

