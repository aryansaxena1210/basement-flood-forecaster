import csv
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
input_file = ROOT / "data" / "processed" / "dataset_c2_windows.csv"
weather_file = ROOT / "data" / "processed" / "extra-features" / "extra_weather_daily.csv"
output_file = ROOT / "data" / "processed" / "extra-features" / "dataset_c2_windows_with_extra_features.csv"

EXTRA = [
    "tmax_f_max",
    "tmin_f_min",
    "wind_mph_avg",
    "snow_in_sum",
    "snow_depth_in_end",
    "thunderstorm_any",
    "humidity_pct_avg",
]

with open(weather_file, newline="") as f:
    weather = {row["date"]: row for row in csv.DictReader(f)}

with open(input_file, newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(fieldnames + EXTRA)

    for row in rows:
        start = date.fromisoformat(row["start_date"])
        days = [weather[(start + timedelta(days=i)).isoformat()] for i in range(3)]

        if days[2]["date"] != row["end_date"]:
            raise ValueError(f"Window does not end on end_date: {row['start_date']}")

        tmax_max = max(float(d["tmax_f"]) for d in days)
        tmin_min = min(float(d["tmin_f"]) for d in days)
        wind_avg = sum(float(d["wind_mph"]) for d in days) / 3
        snow_sum = sum(float(d["snow_in"]) for d in days)
        snow_depth_end = days[2]["snow_depth_in"]
        thunder_any = max(int(d["thunderstorm"]) for d in days)
        humidity_avg = sum(float(d["humidity_pct"]) for d in days) / 3

        writer.writerow(
            [row[c] for c in fieldnames]
            + [f"{tmax_max:g}", f"{tmin_min:g}", f"{wind_avg:.2f}", f"{snow_sum:.1f}", snow_depth_end, thunder_any, f"{humidity_avg:.1f}"]
        )
