"""Join 311 daily counts with O'Hare/Midway rain into data/processed/daily.csv (see docs/data_contract.md)."""
import csv
import json
from datetime import date, timedelta

from flood_events import find_events

START = date(2019, 3, 1)  # the 311 category was still ramping up in Jan-Feb 2019


def load_rain(path):
    rain = {}
    for r in csv.DictReader(open(path)):
        if r["PRCP"] != "":
            rain[date.fromisoformat(r["DATE"])] = float(r["PRCP"])
    return rain


ohare = load_rain("data/raw/noaa/ohare_2018_now.csv")
midway = load_rain("data/raw/noaa/midway_2018_now.csv")
complaints = {
    date.fromisoformat(r["day"][:10]): int(r["n"])
    for r in json.load(open("data/raw/311/daily_counts_2018_now.json"))
}

# The latest 311 day is still filling in, so it is dropped.
end = min(max(ohare), max(midway), max(complaints) - timedelta(1))

days, counts, prcp = [], {}, {}
d = START
while d <= end:
    days.append(d)
    counts[d] = complaints.get(d, 0)
    if d in ohare and d in midway:
        prcp[d] = max(ohare[d], midway[d])
    else:
        prcp[d] = ohare.get(d, midway.get(d, ""))
    d += timedelta(1)

# is_spike covers each event from its first to its last flood day, quiet days in between included.
spike_days = set()
for e in find_events(counts):
    d = e[0]
    while d <= e[-1]:
        spike_days.add(d)
        d += timedelta(1)

rows = [[d.isoformat(), counts[d], prcp[d], int(d in spike_days)] for d in days]

with open("data/processed/daily.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "complaint_count", "prcp_in", "is_spike"])
    w.writerows(rows)
print(f"{len(rows)} days, {rows[0][0]} to {rows[-1][0]} -> data/processed/daily.csv")
