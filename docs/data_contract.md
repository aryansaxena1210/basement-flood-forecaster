# Data Contract: `daily.csv`

`data/processed/daily.csv` is the hand-off between the data layer (Persons 1 and 2) and everyone who models or checks it (Persons 3, 4, and 6). Code against what is written here.

**How it's made:** `fetch_311.py` and `fetch_noaa.py` download into `data/raw/`, then `build_daily.py` joins them into `daily.csv`, all in `src/data/`. The file is git-ignored. The shared link is in the README.

**Until the real file exists**, use `data/sample/daily_sample.csv`. It has the same columns but is fake, with different dates and random storms. Never quote results from it.

## Shape

One row per calendar day, from **2019-03-01** to the last complete day (currently 2026-10-20), sorted by date, no gaps, no blanks.

## Columns

| Column | Type | What it is |
|---|---|---|
| `date` | YYYY-MM-DD | Calendar day, Chicago time |
| `complaint_count` | int | Chicago 311 requests of type `Water in Basement Complaint`, duplicates removed (`duplicate=false`), counted by the day they were created. Days with none are 0. |
| `prcp_in` | float | Rain that day in inches: the **larger** of the O'Hare (`USW00094846`) and Midway (`USW00014819`) daily totals. If one is blank, the other is used. |
| `is_spike` | 0 or 1 | 1 if the day is inside a flood event, including quiet days between flood days. Rule: [`flood_events.md`](flood_events.md). **For scoring and plots only. Never a model input.** |

Example rows (real data):

```
date,complaint_count,prcp_in,is_spike
2023-07-01,11,0.47,0
2023-07-02,1337,4.68,1
2023-07-03,1353,0.0,1
```

## Read this before you use it

1. **Dry days can have huge counts.** Complaints stay high for 13 to 20 days after the biggest floods. July 3, 2023 has 1,353 complaints and 0 rain. Same-day rain alone will mislead you, so use rain from the days before.
2. **A normal day is about 8 complaints** (median). Flood days run from 100 to 3,653.
3. **Spike days are rare:** 96 of 2,791 days. 6 events are "big" (500+ on the busiest day).
4. **Recent days can still change.** The newest 311 day is dropped because it is still filling in (Oct 23 showed 2 complaints, then 12 a few days later). Rerun the fetch before relying on the last few days.
5. **The two airports can miss a storm.** For Aug 2025 the stations show about 1.6 in while news reported 4 to 6 in. Rain here is a floor, not the full truth.

## Not in this file

| Thing | Where it lives |
|---|---|
| Rain over the last 1, 3, 7, 14 days, month, day of year | `data/processed/features.csv` (Person 3) |
| One row per flood event, with `confirmed` and `notes` | `data/labels/flood_events.csv` (Persons 2 and 1) |
| Forecast rain | `src/data/forecast.py` (Person 1) |
| Each station's rain on its own, hourly rain | Not used |

## Checking it

`python notebooks/p2_311/check_daily.py` verifies the columns, gaps, blank rain, negative counts, and zero-complaint days.

## Changing it

Changing a column or what it means breaks other people's code. Tell Persons 3 and 4 first, and update this file in the same pull request.
