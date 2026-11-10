import csv
from datetime import date, timedelta
from pathlib import Path

input_file = Path("data/processed/daily.csv")
output_c1 = Path("data/processed/dataset_c1_windows.csv")
output_c2 = Path("data/processed/dataset_c2_windows.csv")

# Read the original daily dataset
with open(input_file, newline="") as f:
	rows = list(csv.DictReader(f))

# Store data using the date as the key
daily = {}

for row in rows:
	day = date.fromisoformat(row["date"])

	if day in daily:
		raise ValueError(f"Duplicate date: {day}")

	daily[day] = row

# Prepare both datasets
c1_rows = []
c2_rows = []

for start in sorted(daily):
	days = [start + timedelta(days=i) for i in range(3)]

	# Only use complete 3-day windows
	if not all(day in daily for day in days):
		continue

	window = [daily[day] for day in days]

	# Sum complaints across all three days
	complaints_3days = sum(int(row["complaint_count"]) for row in window)

	# C1: Rainfall on the starting day only
	rain_1day = window[0]["prcp_in"]

	# C2: Total rainfall across three days
	rain_values = [row["prcp_in"] for row in window]
	if all(value != "" for value in rain_values):
		rain_3days = sum(float(value) for value in rain_values)
	else:
		rain_3days = ""

	end = days[-1].isoformat()

	c1_rows.append(
		[start.isoformat(), end, rain_1day, complaints_3days]
	)
	c2_rows.append(
		[start.isoformat(), end, rain_3days, complaints_3days]
	)

# Save Dataset C1
with open(output_c1, "w", newline="") as f:
	writer = csv.writer(f, lineterminator="\n")
	writer.writerow(
		["start_date", "end_date", "rainfall_1day_in", "complaints_3days"]
	)
	writer.writerows(c1_rows)

# Save Dataset C2
with open(output_c2, "w", newline="") as f:
	writer = csv.writer(f, lineterminator="\n")
	writer.writerow(
		["start_date", "end_date", "rainfall_3days_in", "complaints_3days"]
	)
	writer.writerows(c2_rows)

print("Dataset C1 created:", output_c1)
print("Dataset C2 created:", output_c2)
print("Total windows:", len(c1_rows))
