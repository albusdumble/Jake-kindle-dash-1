import requests
from icalendar import Calendar
from datetime import datetime, timezone
import json

ICS_URL = "https://p157-caldav.icloud.com/published/2/MjAzMDk4MjAyNTcyMDMwOWelqCDmoGrZl0HbDRwh4THxwVTjex_ugi0QuWfxMzqeyjBGGFltleGeYl57ChEM7SaryzOAF7EjZcsTepi0Pwg"
OUTPUT_FILE = "calendar.json"
EVENT_COUNT = 4

# Fetch ICS
resp = requests.get(ICS_URL)
resp.raise_for_status()
cal = Calendar.from_ical(resp.text)

# Parse events
events = []
now = datetime.now(timezone.utc)

for component in cal.walk():
    if component.name == "VEVENT":
        start = component.get('dtstart').dt
        summary = str(component.get('summary'))
        if isinstance(start, datetime) and start >= now:
            events.append({"date": start.isoformat(), "summary": summary})

# Sort by date and take first N
events.sort(key=lambda e: e["date"])
events = events[:EVENT_COUNT]

# Write JSON
with open(OUTPUT_FILE, "w") as f:
    json.dump(events, f, indent=2)

print(f"Wrote {len(events)} upcoming events to {OUTPUT_FILE}")
