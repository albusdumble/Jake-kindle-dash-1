from datetime import datetime, date, timedelta
import icalendar
import requests
import json

# Fetch and parse ICS file
url = ""https://p157-caldav.icloud.com/published/2/MjAzMDk4MjAyNTcyMDMwOWelqCDmoGrZl0HbDRwh4THxwVTjex_ugi0QuWfxMzqeyjBGGFltleGeYl57ChEM7SaryzOAF7EjZcsTepi0Pwg""
r = requests.get(url)
cal = icalendar.Calendar.from_ical(r.text)

today = date.today()
events = []

for component in cal.walk():
    if component.name == "VEVENT":
        start = component.get("dtstart").dt
        summary = str(component.get("summary"))

        # Normalize start to a date
        if isinstance(start, datetime):
            start_date = start.date()
        else:
            start_date = start

        # Only show events from today forward
        if start_date >= today:
            # Convert to local time if needed
            if isinstance(start, datetime):
                start_time = start.strftime("%I:%M %p")
            else:
                start_time = ""

            # Add leading zero formatting (already handled by %I)
            formatted_date = start.strftime("%b %d") if isinstance(start, datetime) else start.strftime("%b %d")
            events.append(f"{formatted_date} {start_time} - {summary}")

# Sort and save
events.sort()
with open("calendar.json", "w") as f:
    json.dump(events[:5], f, indent=2)
