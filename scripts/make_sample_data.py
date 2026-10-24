"""Generate synthetic data/sample/daily_sample.csv matching docs/data_contract.md."""
import csv
import math
import random
from datetime import date, timedelta

random.seed(42)
start, end = date(2018, 1, 1), date(2026, 9, 30)
days = [start + timedelta(d) for d in range((end - start).days + 1)]
n = len(days)

prcp = [round(random.gammavariate(1.2, 0.35), 2) if random.random() < 0.25 else 0.0 for _ in days]
storms = random.sample(range(n), 9)
for i in storms:
    prcp[i] = round(random.uniform(2.5, 6.0), 2)

rows = []
for i, d in enumerate(days):
    season = 1 + 0.5 * math.sin((d.timetuple().tm_yday - 80) / 365 * 2 * math.pi)
    wet_week = sum(prcp[max(0, i - 6):i + 1])
    lam = 8 * season + 6 * prcp[i] + 0.5 * wet_week
    count = max(0, round(random.gauss(lam, math.sqrt(lam))))
    if i in storms:
        count += random.randint(150, 600)
    rows.append([
        d.isoformat(), count, prcp[i],
        int(i in storms),
    ])

with open("data/sample/daily_sample.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "complaint_count", "prcp_in", "is_spike"])
    w.writerows(rows)
print(len(rows), "rows,", len(storms), "spike days")
