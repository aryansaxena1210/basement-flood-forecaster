# Extra Weather Features

The four experimental datasets (`dataset_b`, `c1`, `c2`, `d`, see [`merging_strategies.md`](merging_strategies.md)) have copies with 7 more weather columns. The originals are unchanged.

Files are in `data/processed/extra-features/`, named `<original name>_with_extra_features.csv`. Row counts and original columns match the originals. The extra columns are added at the end. No blanks.

## Columns added

| Daily files (b, d) | 3-day window files (c1, c2) | Meaning |
|---|---|---|
| `tmax_f` | `tmax_f_max` | Daily high, °F (window: highest of the 3 days) |
| `tmin_f` | `tmin_f_min` | Daily low, °F (window: lowest of the 3 days) |
| `wind_mph` | `wind_mph_avg` | Average wind speed, mph (window: average) |
| `snow_in` | `snow_in_sum` | Snowfall, inches (window: total) |
| `snow_depth_in` | `snow_depth_in_end` | Snow on the ground, inches (window: last day) |
| `thunderstorm` | `thunderstorm_any` | 1 if a thunderstorm was reported (window: any day) |
| `humidity_pct` | `humidity_pct_avg` | Average relative humidity, % (window: average) |

In `d`, the weather is from `prediction_date` (today), not the target day. Only rain has yesterday/tomorrow columns.

## Where it comes from

- Temperature, wind, snow, thunderstorm: NOAA daily summaries (same API and stations as rain). O'Hare first, Midway when O'Hare is blank.
- Thunderstorm: NOAA only writes the flag on days a storm was reported, so blank means 0.
- Humidity: Iowa Environmental Mesonet (`ORD`), averaged per day. NOAA's hourly dataset stops in Aug 2025, and IEM does not. IEM re-publishes the same O'Hare airport reports. On days both have data they differ by about 1 point on average.
- Days run midnight to midnight local standard time (UTC-6), matching NOAA's daily values.

The merged per-day file is `data/processed/extra-features/extra_weather_daily.csv` (2019-03-01 to 2026-11-13).

## Read this before you use it

1. **Same-day weather, not forecasts.** The live tool would need a forecast for each one. Only forecast rain is built today.
2. **Most of these are weak on their own.** Rank correlation with same-day complaints, before humidity was added: thunderstorm 0.24, tmin 0.11, tmax 0.07, wind 0.05, snow about 0. Rain is 0.27. Humidity was 0.25 on the days NOAA had it, but it overlaps with rain (0.58).
3. **Snow columns are mostly 0.** Snow fell on 184 of 2,791 days.
4. **Scale the columns before Lasso or Ridge.** Temperature and rain are on very different scales.

## Re-running

From the repo root, in this order:

```
python src/data/extra-features/fetch_extra_weather.py
python src/data/extra-features/fetch_hourly_humidity.py
python src/data/extra-features/add_extra_to_dataset_b.py
python src/data/extra-features/add_extra_to_dataset_c1.py
python src/data/extra-features/add_extra_to_dataset_c2.py
python src/data/extra-features/add_extra_to_dataset_d.py
```
