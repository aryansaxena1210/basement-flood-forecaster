import csv
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw" / "iem"
RAW_DIR.mkdir(parents=True, exist_ok=True)
weather_file = ROOT / "data" / "processed" / "extra-features" / "extra_weather_daily.csv"

# Iowa Environmental Mesonet archive of O'Hare (ORD) hourly airport reports
today = date.today()
url = (
    "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=ORD&data=relh"
    f"&year1=2019&month1=3&day1=1&year2={today.year}&month2={today.month}&day2={today.day}"
    "&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3"
)
text = urllib.request.urlopen(url, timeout=300).read().decode("utf-8")
(RAW_DIR / "ohare_hourly_relh.csv").write_text(text, encoding="utf-8")

# Daily weather is local standard time (UTC-6)
readings = defaultdict(list)
for row in csv.DictReader(text.splitlines()):
    if row["relh"] in ("M", ""):
        continue
    local = datetime.strptime(row["valid"], "%Y-%m-%d %H:%M") - timedelta(hours=6)
    readings[local.date().isoformat()].append(float(row["relh"]))

# Add humidity_pct to the merged daily weather file
with open(weather_file, newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = [c for c in reader.fieldnames if c != "humidity_pct"]
    rows = list(reader)

blank = 0
with open(weather_file, "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(fieldnames + ["humidity_pct"])
    for row in rows:
        values = readings.get(row["date"])
        if not values:
            blank += 1
        writer.writerow([row[c] for c in fieldnames] + ["" if not values else f"{sum(values) / len(values):.1f}"])

print("days:", len(rows), "blank humidity:", blank)
