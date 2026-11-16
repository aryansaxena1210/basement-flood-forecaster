"""Sanity checks on data/processed/daily.csv. Run from the repo root after every rebuild."""
import csv
import sys
from collections import Counter
from datetime import date, timedelta

rows = list(csv.DictReader(open("data/processed/daily.csv")))
days = [date.fromisoformat(r["date"]) for r in rows]
counts = [int(r["complaint_count"]) for r in rows]
failures = []

if list(rows[0]) != ["date", "complaint_count", "prcp_in", "is_spike"]:
    failures.append("columns do not match docs/data_contract.md")
if not all(b - a == timedelta(1) for a, b in zip(days, days[1:])):
    failures.append("dates are not sorted and gap-free")
if any(r["prcp_in"] == "" for r in rows):
    failures.append("blank rain values")
if any(c < 0 for c in counts):
    failures.append("negative complaint counts")

print(f"{len(rows)} days, {days[0]} to {days[-1]}")
print("last 3 days:", [(str(d), c) for d, c in zip(days[-3:], counts[-3:])])

zero = [d for d, c in zip(days, counts) if c == 0]
print(f"\nzero-complaint days: {len(zero)}  (a real quiet day is rare; many zeros means the category was not live yet)")
print("  by year-month:", dict(sorted(Counter(f"{d.year}-{d.month:02d}" for d in zero).items())))

print("\ncomplaints per year (a year far off its neighbours deserves a look)")
by_year = Counter()
for d, c in zip(days, counts):
    by_year[d.year] += c
for y, total in sorted(by_year.items()):
    print(f"  {y}: {total}")

print("\nFAILURES:", failures if failures else "none")
sys.exit(1 if failures else 0)
