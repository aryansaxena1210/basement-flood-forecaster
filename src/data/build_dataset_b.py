
import csv
from datetime import date, timedelta
from pathlib import Path

# Input and output file paths
input_file = Path("data/processed/daily.csv")
output_file = Path("data/processed/dataset_b_daily_lags.csv")

# Read the existing daily dataset
with open(input_file, "r", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Make a dictionary to find rainfall by date
rain_by_date = {}

for row in rows:
    day = date.fromisoformat(row["date"])

    if day in rain_by_date:
        raise ValueError(f"Duplicate date: {day}")

    rain_by_date[day] = row["prcp_in"]

# Create the new Dataset B
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")

    writer.writerow([
        "date",
        "rainfall_today",
        "rainfall_1_day_ago",
        "rainfall_2_days_ago",
        "complaint_count"
    ])

    for row in rows:
        day = date.fromisoformat(row["date"])

        rain_today = rain_by_date.get(day, "")
        rain_yesterday = rain_by_date.get(
            day - timedelta(days=1), ""
        )
        rain_two_days_ago = rain_by_date.get(
            day - timedelta(days=2), ""
        )

        writer.writerow([
            row["date"],
            rain_today,
            rain_yesterday,
            rain_two_days_ago,
            row["complaint_count"]
        ])

print(f"Dataset B created: {output_file}")
print(f"Total rows: {len(rows)}")
