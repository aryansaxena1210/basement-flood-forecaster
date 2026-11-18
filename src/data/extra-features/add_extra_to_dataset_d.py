import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
input_file = ROOT / "data" / "processed" / "dataset_d_next_day_forecast.csv"
weather_file = ROOT / "data" / "processed" / "extra-features" / "extra_weather_daily.csv"
output_file = ROOT / "data" / "processed" / "extra-features" / "dataset_d_next_day_forecast_with_extra_features.csv"

EXTRA = ["tmax_f", "tmin_f", "wind_mph", "snow_in", "snow_depth_in", "thunderstorm"]

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
        # Weather of the prediction day (today), not the target day
        day = weather[row["prediction_date"]]
        writer.writerow([row[c] for c in fieldnames] + [day[c] for c in EXTRA])
