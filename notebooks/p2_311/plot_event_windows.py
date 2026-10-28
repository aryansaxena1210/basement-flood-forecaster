"""Per flood event: max daily rain (6 days before the start through the event's last flood day) vs complaints over the next 7 and 14 days, stopping at the next event. Run from the repo root."""
import csv
import os
from datetime import date, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FLOOD_CUTOFF = 100  # proposed flood rule, not final
MERGE_GAP = 2
BIG_PEAK = 500

rows = list(csv.DictReader(open("data/processed/daily.csv")))
days = [date.fromisoformat(r["date"]) for r in rows]
counts = {d: int(r["complaint_count"]) for d, r in zip(days, rows)}
rain = {d: float(r["prcp_in"]) for d, r in zip(days, rows)}

events = []
for d in days:
    if counts[d] >= FLOOD_CUTOFF:
        if events and (d - events[-1][-1]).days <= MERGE_GAP:
            events[-1].append(d)
        else:
            events.append([d])

points = []
for i, e in enumerate(events):
    start, end = e[0], e[-1]
    if start + timedelta(13) > days[-1] or start - timedelta(6) < days[0]:
        continue
    next_start = events[i + 1][0] if i + 1 < len(events) else days[-1] + timedelta(1)
    span = (end - start).days + 7
    max_rain = max(rain[start - timedelta(6) + timedelta(k)] for k in range(span))
    sum7 = sum(counts[start + timedelta(k)] for k in range(7) if start + timedelta(k) < next_start)
    sum14 = sum(counts[start + timedelta(k)] for k in range(14) if start + timedelta(k) < next_start)
    peak = max(counts[d] for d in e)
    points.append((start, max_rain, sum7, sum14, peak))

print(f"{len(points)} events (of {len(events)}; events too close to the data edges are skipped)")
print(f"{'start':12}{'max rain 7d':>12}{'next 7d':>10}{'next 14d':>10}{'peak':>7}")
for s, mr, s7, s14, pk in points:
    print(f"{s}  {mr:10.2f}{s7:10d}{s14:10d}{pk:7d}")


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    for pos, i in enumerate(order):
        r[i] = pos
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den


fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
for a, idx, label in ((ax[0], 2, "7"), (ax[1], 3, "14")):
    for p in points:
        big = p[4] >= BIG_PEAK
        a.scatter(p[1], p[idx], s=70 if big else 35, color="tab:red" if big else "tab:blue", alpha=0.8)
        if big:
            a.annotate(str(p[0]), (p[1], p[idx]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    rho = spearman([p[1] for p in points], [p[idx] for p in points])
    a.set(yscale="log", xlabel="max single-day rain around the event (in)",
          ylabel=f"total complaints, next {label} days",
          title=f"Next {label} days (rank correlation {rho:.2f})")
    print(f"next {label} days: rank correlation with max rain = {rho:.2f}")
ax[0].scatter([], [], color="tab:red", label=f"big event (peak {BIG_PEAK}+)")
ax[0].scatter([], [], color="tab:blue", label="smaller event")
ax[0].legend()
plt.tight_layout()
os.makedirs("notebooks/p2_311/figures", exist_ok=True)
plt.savefig("notebooks/p2_311/figures/event_windows.png", dpi=90)
print("saved notebooks/p2_311/figures/event_windows.png")
