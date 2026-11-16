"""Bar chart of typical complaints and flood-day share by recent rain. Run from the repo root."""
import csv
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("data/processed/daily.csv")))
n = [int(r["complaint_count"]) for r in rows]
rain = [float(r["prcp_in"]) for r in rows]
rain3 = [sum(rain[max(0, i - 2):i + 1]) for i in range(len(rain))]

bins = [("dry", 0, 0.001), ("0-0.25", 0.001, 0.25), ("0.25-0.5", 0.25, 0.5),
        ("0.5-1", 0.5, 1), ("1-2", 1, 2), ("2+", 2, 99)]
labels, medians, shares, sizes = [], [], [], []
for lab, lo, hi in bins:
    v = [c for c, r in zip(n, rain3) if lo <= r < hi]
    labels.append(lab)
    medians.append(statistics.median(v))
    shares.append(100 * sum(c >= 100 for c in v) / len(v))
    sizes.append(len(v))

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].bar(labels, medians, color="tab:blue")
ax[0].set(title="Typical complaints per day", xlabel="rain over the last 3 days (in)", ylabel="median complaints")
ax[1].bar(labels, shares, color="tab:red")
ax[1].set(title="Share of days with 100+ complaints", xlabel="rain over the last 3 days (in)", ylabel="% of days")
for a in ax:
    for i, s in enumerate(sizes):
        a.annotate(f"{s} days", (i, 0), ha="center", va="bottom", fontsize=8, color="white")
plt.tight_layout()
os.makedirs("notebooks/p2_311/figures", exist_ok=True)
plt.savefig("notebooks/p2_311/figures/complaints_by_rain.png", dpi=90)
print("saved notebooks/p2_311/figures/complaints_by_rain.png")
