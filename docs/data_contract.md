# Data Contract

Persons 1 and 2 produce `data/processed/daily.csv`. Persons 3 and 4 consume it.
Until the real file exists, use `data/sample/daily_sample.csv` (synthetic, same columns).

One row per calendar day, sorted ascending by `date`, no gaps.

| Column | Type | Description |
|---|---|---|
| `date` | date (YYYY-MM-DD) | Calendar day (America/Chicago) |
| `complaint_count` | int | Chicago 311 `Water in Basement Complaint` requests created that day |
| `prcp_in` | float | Daily total precipitation, inches: average of O'Hare and Midway (O'Hare alone when Midway is blank) |
| `is_spike` | int (0/1) | 1 if the day belongs to a verified flood event |

Rules:
- Missing rain values stay empty (NaN). Do not fill with 0.
- Rolling/cumulative rain features (3-day, 7-day, etc.) are NOT in this file. Person 3 builds them into `data/processed/features.csv`.
- Spike days come from the verified event list in `data/labels/flood_events.csv` (owned by Person 2).
