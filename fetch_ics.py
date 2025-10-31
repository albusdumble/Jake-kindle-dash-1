#!/usr/bin/env python3
import requests
from icalendar import Calendar
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import json
import sys

# -------- CONFIG --------
ICS_URL = "https://p157-caldav.icloud.com/published/2/MjAzMDk4MjAyNTcyMDMwOWelqCDmoGrZl0HbDRwh4THxwVTjex_ugi0QuWfxMzqeyjBGGFltleGeYl57ChEM7SaryzOAF7EjZcsTepi0Pwg"
LOCAL_TZ = ZoneInfo("America/Chicago")
MAX_EVENTS = 5

# -------- FETCH ICS --------
try:
    resp = requests.get(ICS_URL, timeout=20)
    resp.raise_for_status()
except Exception as e:
    print("Error fetching ICS:", e, file=sys.stderr)
    sys.exit(1)

cal = Calendar.from_ical(resp.text)

# -------- NOW / FILTER BOUNDARY --------
now_local = datetime.now(LOCAL_TZ)
today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)

parsed = []

# -------- PARSE EVENTS --------
for comp in cal.walk():
    if comp.name != "VEVENT":
        continue
    try:
        dt = comp.get("DTSTART").dt
    except Exception:
        continue

    summary = comp.get("SUMMARY")
    if summary is None:
        summary = "No title"
    else:
        summary = str(summary)

    # Normalize start as a datetime (timezone-aware in LOCAL_TZ) and also track if all-day
    is_all_day = False
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # all-day: treat as midnight local time for sorting/display
        is_all_day = True
        local_start = datetime.combine(dt, time.min).replace(tzinfo=LOCAL_TZ)
    else:
        # datetime
        local_dt = dt
        if local_dt.tzinfo is None:
            # Assume floating/local times are already local — assign LOCAL_TZ
            local_dt = local_dt.replace(tzinfo=LOCAL_TZ)
        # convert to local tz
        local_start = local_dt.astimezone(LOCAL_TZ)

    # Only keep events from today onward
    if local_start >= today_start:
        parsed.append({
            "dt": local_start,
            "all_day": is_all_day,
            "summary": summary
        })

# -------- SORT & LIMIT --------
parsed.sort(key=lambda x: x["dt"])
parsed = parsed[:MAX_EVENTS]

# -------- FORMAT OUTPUT STRINGS --------
def fmt_month_day(dtm):
    return dtm.strftime("%b %d")  # e.g., "Oct 31"

def fmt_time(dtm):
    # %I gives 01..12 with leading zero, exactly what you asked for
    return dtm.strftime("%I:%M %p")  # e.g., "03:30 PM" or "10:45 AM"

out = []
for e in parsed:
    dt = e["dt"]
    summary = e["summary"]
    if e["all_day"]:
        out.append(f"{fmt_month_day(dt)} - {summary}")
    else:
        out.append(f"{fmt_month_day(dt)} {fmt_time(dt)} - {summary}")

# -------- WRITE calendar.json --------
with open("calendar.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(out)} upcoming events to calendar.json")
