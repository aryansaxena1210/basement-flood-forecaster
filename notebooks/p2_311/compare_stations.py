"""Compare O Hare, Midway, and their average as predictors of daily complaints. Run from the repo root."""
import csv, json
from datetime import date, timedelta

def load_rain(path):
    d = {}
    for r in csv.DictReader(open(path)):
        if r["PRCP"] != "":
            d[date.fromisoformat(r["DATE"])] = float(r["PRCP"])
    return d

oh = load_rain("data/raw/noaa/ohare_2018_now.csv")
mw = load_rain("data/raw/noaa/midway_2018_now.csv")
cmpl = {date.fromisoformat(x["day"][:10]): int(x["n"]) for x in json.load(open("data/raw/311/daily_counts_2018_now.json"))}

days = [date(2019,1,1) + timedelta(i) for i in range((date(2026,10,20) - date(2019,1,1)).days + 1)]

def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0]*len(v); i = 0
    while i < len(order):
        j = i
        while j+1 < len(order) and v[order[j+1]] == v[order[i]]: j += 1
        for k in range(i, j+1): r[order[k]] = (i+j)/2
        i = j+1
    return r

def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(a); ma = sum(ra)/n; mb = sum(rb)/n
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb))
    den = (sum((x-ma)**2 for x in ra) * sum((y-mb)**2 for y in rb)) ** 0.5
    return num/den

y = [cmpl.get(d, 0) for d in days]
def series(f): return [f(d) for d in days]
def r(src, d): return src.get(d, 0.0)

variants = {
    "O'Hare only":   lambda d: r(oh, d),
    "Midway only":   lambda d: r(mw, d),
    "Average":       lambda d: (r(oh, d) + r(mw, d)) / 2,
    "Max of two":    lambda d: max(r(oh, d), r(mw, d)),
}
print("missing days in 2019+: ohare", sum(d not in oh for d in days), " midway", sum(d not in mw for d in days))
print("days where stations differ by >1 in:", sum(abs(r(oh,d)-r(mw,d)) > 1 for d in days))
print()
print("Spearman correlation with daily complaints (higher is better)")
print(f"{'':14}{'same day':>10}{'rain 2d':>10}{'rain 3d':>10}{'prior day':>11}")
for name, f in variants.items():
    same = spearman(series(f), y)
    r2 = spearman(series(lambda d: f(d) + f(d - timedelta(1))), y)
    r3 = spearman(series(lambda d: sum(f(d - timedelta(k)) for k in range(3))), y)
    prev = spearman(series(lambda d: f(d - timedelta(1))), y)
    print(f"{name:14}{same:10.3f}{r2:10.3f}{r3:10.3f}{prev:11.3f}")
