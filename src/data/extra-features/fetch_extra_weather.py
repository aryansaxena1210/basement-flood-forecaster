import csv
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data" / "raw" / "noaa"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
STATIONS = {"ohare": "USW00094846", "midway": "USW00014819"}
TYPES = ["TMAX", "TMIN", "AWND", "SNOW", "SNWD", "WT03"]

# Download each station
data = {}
for name, station in STATIONS.items():
    params = {
        "dataset": "daily-summaries",
        "stations": station,
        "startDate": "2019-03-01",
        "endDate": date.today().isoformat(),
        "dataTypes": ",".join(TYPES),
        "units": "standard",
        "format": "csv",
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    text = urllib.request.urlopen(url, timeout=120).read().decode("utf-8")
    (OUT_DIR / f"{name}_extra_weather.csv").write_text(text, encoding="utf-8")
    data[name] = {r["DATE"]: r for r in csv.DictReader(text.splitlines())}

# Merge: O'Hare first, Midway when O'Hare is blank
COLUMNS = {"TMAX": "tmax_f", "TMIN": "tmin_f", "AWND": "wind_mph", "SNOW": "snow_in", "SNWD": "snow_depth_in"}
merged_dir = ROOT / "data" / "processed" / "extra-features"
merged_dir.mkdir(parents=True, exist_ok=True)

with open(merged_dir / "extra_weather_daily.csv", "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["date"] + list(COLUMNS.values()) + ["thunderstorm"])
    for day in sorted(data["ohare"]):
        oh = data["ohare"][day]
        mid = data["midway"].get(day, {})
        row = [day]
        for t in COLUMNS:
            row.append(oh.get(t, "") or mid.get(t, ""))
        # blank WT03 means no thunderstorm reported
        row.append(1 if (oh.get("WT03", "") or mid.get("WT03", "")) else 0)
        writer.writerow(row)

# Blank counts per station
for name, rows in data.items():
    print(name, "rows:", len(rows))
    for t in TYPES:
        blanks = sum(1 for r in rows.values() if r.get(t, "") == "")
        print("  ", t, "blank:", blanks)
