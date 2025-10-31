import requests
from icalendar import Calendar
from datetime import datetime
from zoneinfo import ZoneInfo
import json

# ---- SETTINGS ----
ics_url = "https://p157-caldav.icloud.com/published/2/MjAzMDk4MjAyNTcyMDMwOWelqCDmoGrZl0HbDRwh4THxwVTjex_ugi0QuWfxMzqeyjBGGFltleGeYl57ChEM7SaryzOAF7EjZcsTepi0Pwg"
local_tz = ZoneInfo("America/Chicago")

# ---- FETCH ----
response = requests.get(ics_url)
response.raise_for_status()
cal = Calendar.from_ical(response.text)

now = datetime.now(local_tz)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

events = []

# ---- PARSE EVENTS ----
for component in cal.walk():
    if component.name == "VEVENT":
        start = component.get("DTSTART").dt
        summary = str(component.get("SUMMARY"))

        # Ensure timezone-aware datetimes
        if isinstance(start, datetime):
            if start.tzinfo is None:
                start = start.replace(tzinfo=local_tz)
            local_start = start.astimezone(local_tz)

            # Only include events today or later
            if local_start >= today_start:
                events.append({
                    "date": local_start.isoformat(),
                    "summary": summary
                })

# ---- SORT & TRIM ----
events = sorted(events, key=lambda e: e["date"])[:5]

# ---- WRITE OUTPUT ----
with open("calendar.json", "w") as f:
    json.dump(events, f, indent=2)

print(f"Wrote {len(events)} upcoming events to calendar.json")
