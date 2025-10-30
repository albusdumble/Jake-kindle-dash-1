import requests
from icalendar import Calendar
from datetime import datetime, timezone, timedelta, date
import json

ics_url = "https://p157-caldav.icloud.com/published/2/MjAzMDk4MjAyNTcyMDMwOWelqCDmoGrZl0HbDRwh4THxwVTjex_ugi0QuWfxMzqeyjBGGFltleGeYl57ChEM7SaryzOAF7EjZcsTepi0Pwg"

response = requests.get(ics_url)
response.raise_for_status()

cal = Calendar.from_ical(response.text)
now = datetime.now(timezone.utc)
today = date.today()

events = []

for component in cal.walk():
    if component.name == "VEVENT":
        start = component.get("DTSTART").dt
        summary = str(component.get("SUMMARY"))
        
        # Normalize date-only to midnight UTC
        if isinstance(start, datetime) and start > now:
            local_start = start.astimezone(ZoneInfo("America/Chicago"))
            events.append({
                "date": local_start.isoformat(),
                "summary": summary
            })
        # Only include events today or later
        if start.date() >= today:
            events.append({"date": start.isoformat(), "summary": summary})

# Sort and limit
events = sorted(events, key=lambda e: e["date"])[:5]

with open("calendar.json", "w") as f:
    json.dump(events, f, indent=2)

print(f"Wrote {len(events)} upcoming events to calendar.json")
