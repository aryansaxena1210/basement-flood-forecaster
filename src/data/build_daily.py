"""Join 311 daily counts with O'Hare/Midway rain into data/processed/daily.csv (see docs/data_contract.md)."""
import csv
import json
from datetime import date, timedelta

START = date(2019, 1, 1)
SPIKE_CUTOFF = 100  # placeholder until the rule in docs/flood_events.md is final


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

rows = []
d = START
while d <= end:
    if d in ohare and d in midway:
        prcp = round((ohare[d] + midway[d]) / 2, 3)
    else:
        prcp = ohare.get(d, midway.get(d, ""))
    count = complaints.get(d, 0)
    rows.append([d.isoformat(), count, prcp, int(count >= SPIKE_CUTOFF)])
    d += timedelta(1)

with open("data/processed/daily.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "complaint_count", "prcp_in", "is_spike"])
    w.writerows(rows)
print(f"{len(rows)} days, {rows[0][0]} to {rows[-1][0]} -> data/processed/daily.csv")
