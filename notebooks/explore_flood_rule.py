"""Look at daily complaint counts to choose the flood cutoff. Run from the repo root."""
import csv
import os
import statistics
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("data/processed/daily.csv")))
days = [date.fromisoformat(r["date"]) for r in rows]
n = [int(r["complaint_count"]) for r in rows]
rain = [float(r["prcp_in"]) for r in rows]
os.makedirs("notebooks/figures", exist_ok=True)

q = statistics.quantiles(n, n=100)
print(f"median {statistics.median(n)}  mean {statistics.mean(n):.1f}  p90 {q[89]:.0f}  p95 {q[94]:.0f}  p99 {q[98]:.0f}  max {max(n)}")

print("\nmedian complaints per day, by month (is a fixed cutoff fair across seasons?)")
for m in range(1, 13):
    v = [c for d, c in zip(days, n) if d.month == m]
    print(f"  {m:2d}: median {statistics.median(v):5.1f}   p90 {statistics.quantiles(v, n=10)[8]:6.1f}")

print("\ndays above each cutoff, per year")
cuts = [30, 50, 100, 200]
print("  year " + "".join(f"{'>='+str(c):>7}" for c in cuts))
for y in range(2019, 2027):
    print(f"  {y} " + "".join(f"{sum(1 for d, c in zip(days, n) if d.year == y and c >= k):7d}" for k in cuts))

fig, ax = plt.subplots(2, 2, figsize=(14, 9))

ax[0, 0].semilogy([d for d in days], [max(c, 0.8) for c in n], lw=0.6)
for k, col in zip([30, 50, 100], ["tab:green", "tab:orange", "tab:red"]):
    ax[0, 0].axhline(k, color=col, ls="--", lw=0.8, label=f"cutoff {k}")
ax[0, 0].set(title="Daily complaints (log scale)", ylabel="complaints/day")
ax[0, 0].legend()

ax[0, 1].hist(n, bins=[0, 2, 4, 6, 8, 10, 15, 20, 30, 50, 100, 200, 500, 1000, 4000], color="gray")
ax[0, 1].set(xscale="log", yscale="log", title="How many days at each size (log-log)", xlabel="complaints/day", ylabel="days")

ax[1, 0].scatter(rain, [max(c, 0.8) for c in n], s=6, alpha=0.4)
ax[1, 0].set(yscale="log", title="Same-day rain vs complaints", xlabel="rain (in)", ylabel="complaints/day")

rain3 = [sum(rain[max(0, i - 2):i + 1]) for i in range(len(rain))]
ax[1, 1].scatter(rain3, [max(c, 0.8) for c in n], s=6, alpha=0.4, color="tab:purple")
ax[1, 1].set(yscale="log", title="3-day rain total vs complaints", xlabel="rain over 3 days (in)", ylabel="complaints/day")

plt.tight_layout()
plt.savefig("notebooks/figures/flood_rule_overview.png", dpi=90)
print("\nsaved notebooks/figures/flood_rule_overview.png")
