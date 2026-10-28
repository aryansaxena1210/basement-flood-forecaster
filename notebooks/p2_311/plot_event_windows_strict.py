"""Per flood event and per window (1, 3, 7, 14 days from the event start), rain, complaints and color all use only days inside that window. Run from the repo root."""
import csv
import os
from datetime import date, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FLOOD_CUTOFF = 100  # proposed flood rule, not final
MERGE_GAP = 2
BIG_DAY = 500
WINDOWS = (1, 3, 7, 14)

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

# per window: list of (start, max rain, total complaints, busiest day)
points = {w: [] for w in WINDOWS}
for i, e in enumerate(events):
    start = e[0]
    if start + timedelta(13) > days[-1] or start - timedelta(6) < days[0]:
        continue
    next_start = events[i + 1][0] if i + 1 < len(events) else days[-1] + timedelta(1)
    for w in WINDOWS:
        window = [start + timedelta(k) for k in range(w) if start + timedelta(k) < next_start]
        last = window[-1]
        max_rain = max(rain[start - timedelta(6) + timedelta(k)] for k in range((last - start).days + 7))
        total = sum(counts[d] for d in window)
        busiest = max(counts[d] for d in window)
        points[w].append((start, max_rain, total, busiest))

print(f"{len(points[1])} events (of {len(events)}; events too close to the data edges are skipped)")
print(f"{'start':12}" + "".join(f"{'rain':>6}{'total':>7}{'best':>6}  |" for w in WINDOWS))
print(f"{'':12}" + "".join(f"{'  ' + str(w) + ' day window':^21}" for w in WINDOWS))
for idx in range(len(points[1])):
    line = f"{points[1][idx][0]}  "
    for w in WINDOWS:
        _, mr, total, best = points[w][idx]
        line += f"{mr:6.2f}{total:7d}{best:6d}  |"
    print(line)


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


fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for a, w in zip(axes.flat, WINDOWS):
    for start, mr, total, best in points[w]:
        big = best >= BIG_DAY
        a.scatter(mr, total, s=70 if big else 35, color="tab:red" if big else "tab:blue", alpha=0.8)
        if big:
            a.annotate(str(start), (mr, total), fontsize=7, xytext=(4, 4), textcoords="offset points")
    rho = spearman([p[1] for p in points[w]], [p[2] for p in points[w]])
    a.set(yscale="log", xlabel=f"max single-day rain, 6 days before the event through day {w}",
          ylabel=f"total complaints, first {w} day{'s' if w > 1 else ''}",
          title=f"First {w} day{'s' if w > 1 else ''} (rank correlation {rho:.2f})")
    print(f"first {w} days: rank correlation with max rain = {rho:.2f}")
axes[0, 0].scatter([], [], color="tab:red", label=f"busiest day inside this window had {BIG_DAY}+")
axes[0, 0].scatter([], [], color="tab:blue", label=f"busiest day inside this window under {BIG_DAY}")
axes[0, 0].legend()
plt.tight_layout()
os.makedirs("notebooks/p2_311/figures", exist_ok=True)
plt.savefig("notebooks/p2_311/figures/event_windows_strict.png", dpi=90)
print("saved notebooks/p2_311/figures/event_windows_strict.png")
