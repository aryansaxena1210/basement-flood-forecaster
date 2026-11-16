"""Download daily Chicago 311 'Water in Basement Complaint' counts (duplicates excluded) to data/raw/311."""
import json
import time
import urllib.parse
import urllib.request

URL = "https://data.cityofchicago.org/resource/v6vf-nfxy.json"
OUT = "data/raw/311/daily_counts_2018_now.json"

params = {
    "$select": "date_trunc_ymd(created_date) as day, count(*) as n",
    "$where": "sr_type='Water in Basement Complaint' AND created_date>='2018-01-01T00:00:00' AND duplicate=false",
    "$group": "day",
    "$order": "day",
    "$limit": "5000",
}
url = URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

for attempt in range(3):
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            rows = json.load(resp)
        break
    except OSError as e:
        print(f"attempt {attempt + 1} failed: {e}")
        time.sleep(5)
else:
    raise SystemExit("311 download failed")

with open(OUT, "w") as f:
    json.dump(rows, f)
print(f"{len(rows)} days, {rows[0]['day'][:10]} to {rows[-1]['day'][:10]} -> {OUT}")
