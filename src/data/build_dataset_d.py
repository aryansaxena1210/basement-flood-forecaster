'''
The idea is to take the rain tomorrow and the date, and mathematically change it a slight
bit making it seem as if there was a forecast for tomorrow's rain. 
Of course it isn't perfect but it is realistic
'''

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

input_file = Path("data/processed/daily.csv")
output_file = Path("data/processed/dataset_d_next_day_forecast.csv")

RANDOM_SEED = 5730 #can reproduce the same dataset
AMOUNT_SPREAD = 0.5
MAX_AMOUNT_DRAW = 2.0
MAX_FORECAST_IN = 6.0
MISS_CHANCE = 0.15
LIGHT_RAIN_IN = 0.25
FALSE_ALARM_CHANCE = 0.10
FALSE_ALARM_MIN_IN = 0.05
FALSE_ALARM_MAX_IN = 0.25


def simulated_forecast(actual_text, target_day):
    if actual_text == "":
        return ""

    actual = float(actual_text)
    rng = random.Random(f"{RANDOM_SEED}-{target_day.isoformat()}")
    amount_draw = rng.gauss(0, 1)
    amount_draw = max(-MAX_AMOUNT_DRAW, min(MAX_AMOUNT_DRAW, amount_draw))
    miss_draw = rng.random()
    false_alarm_draw = rng.random()
    false_alarm_size = rng.random()

    if actual == 0:
        if false_alarm_draw < FALSE_ALARM_CHANCE:
            forecast = FALSE_ALARM_MIN_IN + false_alarm_size * (FALSE_ALARM_MAX_IN - FALSE_ALARM_MIN_IN)
        else:
            forecast = 0.0
    elif actual < LIGHT_RAIN_IN and miss_draw < MISS_CHANCE:
        forecast = 0.0
    else:
        forecast = actual * math.exp(AMOUNT_SPREAD * amount_draw)

    forecast = min(forecast, MAX_FORECAST_IN)
    return f"{forecast:.2f}"

with open(input_file, "r", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

daily = {}

for row in rows:
    day = date.fromisoformat(row["date"])

    if day in daily:
        raise ValueError(f"Duplicate date: {day}")

    daily[day] = row

output_rows = []

for today in sorted(daily):
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    if yesterday not in daily or tomorrow not in daily:
        continue

    output_rows.append([
        today.isoformat(),
        tomorrow.isoformat(),
        daily[yesterday]["prcp_in"],
        daily[today]["prcp_in"],
        daily[tomorrow]["prcp_in"],
        simulated_forecast(daily[tomorrow]["prcp_in"], tomorrow),
        daily[yesterday]["complaint_count"],
        daily[tomorrow]["complaint_count"],
        daily[tomorrow]["is_spike"],
    ])

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")

    writer.writerow([
        "prediction_date",
        "target_date",
        "rain_yesterday_in",
        "rain_today_in",
        "rain_tomorrow_in",
        "rain_tomorrow_forecast_in",
        "complaints_yesterday",
        "complaints_tomorrow",
        "is_spike_tomorrow"
    ])
    writer.writerows(output_rows)

print(f"Dataset D created: {output_file}")
print(f"Total rows: {len(output_rows)}")
