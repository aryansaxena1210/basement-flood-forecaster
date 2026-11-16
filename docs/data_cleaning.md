# Data Cleaning

What I did to the raw data to get `daily.csv`. Scripts are in `src/data/`. Columns are in [`data_contract.md`](data_contract.md).

- **What I count:** only `Water in Basement Complaint`, by the day it was created. Duplicates removed (3,206 of 70,573, or 4.5%).
- **Dropped:** everything before 2019-03-01, because the category was still ramping up (Jan and Feb 2019 had a median of 0 to 1 complaints a day). Also the newest 311 day, because it is still filling in.
- **Filled:** days with no complaints get 0. Midway's 4 blank rain days (2019-05-09, 2021-02-13, 2021-02-15, 2021-02-16) use O'Hare's value.
- **Rain:** the larger of the O'Hare and Midway daily totals. See [`flood_events.md`](flood_events.md) decision 6.
- **Left alone:** complaints not caused by rain (I can't tell them apart; `docs/label_noise.md` measures them), the huge flood days (they are real), and the aftermath days when complaints stay high with no rain.
- **Known limits:** the airports can under-read a storm (Aug 2025: about 1.6 in vs 4 to 6 in in the news), and the last few days of `daily.csv` can still be revised upward.

**Re-run:**
```
python src/data/fetch_311.py
python src/data/fetch_noaa.py          # Person 1
python src/data/build_daily.py
python src/data/build_flood_events.py
```
