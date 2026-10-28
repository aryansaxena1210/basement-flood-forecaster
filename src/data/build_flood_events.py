"""Build data/labels/flood_events.csv from daily.csv using the flood rule (docs/flood_events.md).
Re-running keeps `confirmed` and `notes` for events whose peak date is unchanged."""
import csv
import os
from datetime import date, timedelta

from flood_events import BIG_PEAK, find_events

OUT = "data/labels/flood_events.csv"
COLUMNS = ["event_id", "start_date", "end_date", "peak_date", "peak_count", "total_complaints", "big", "confirmed", "notes"]

counts = {
    date.fromisoformat(r["date"]): int(r["complaint_count"])
    for r in csv.DictReader(open("data/processed/daily.csv"))
}

previous = {}
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT)):
        previous[r["peak_date"]] = (r["confirmed"], r["notes"])

rows = []
for i, e in enumerate(find_events(counts), start=1):
    start, end = e[0], e[-1]
    peak = max(e, key=lambda d: counts[d])
    total = sum(counts[start + timedelta(k)] for k in range((end - start).days + 1))
    confirmed, notes = previous.get(peak.isoformat(), ("", ""))
    rows.append([i, start, end, peak, counts[peak], total, "yes" if counts[peak] >= BIG_PEAK else "no", confirmed, notes])

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(COLUMNS)
    w.writerows(rows)
print(f"{len(rows)} events ({sum(r[6] == 'yes' for r in rows)} big) -> {OUT}")
