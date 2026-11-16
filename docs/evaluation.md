# How the Scoring Works

Owner: Person 4. Code: `src/models/evaluate.py`. Inputs: `src/features/build_features.py`.
Every model in this project (simple, boosted, whatever goes in the API) is scored with this tool, so scores are comparable. Don't change a rule here without telling Persons 3 and 5.

## Quick start

```
python -m src.models.evaluate              # seasonal baseline, rain + calendar inputs
python -m src.models.evaluate --lag 3      # add complaints from 3 days before the target
```

From code, any object with `fit(X, y)` and `predict(X)` works (scikit-learn, XGBoost, LightGBM):

```python
from sklearn.linear_model import Ridge
from src.models.evaluate import evaluate
result = evaluate(lambda: Ridge(alpha=1.0), complaint_lag=None, name="ridge")
result.print()                 # per-year table + per-event table
result.per_year.loc["all"]     # overall numbers
result.predictions             # every test-day prediction, for plots
```

`evaluate` takes a function that *makes* a model, so each test year gets a fresh one.

## What one prediction is

One row per target day D. The target is D's complaint count (`complaint_count` in `daily.csv`, duplicates already removed).

| Input | Meaning |
|---|---|
| `rain_1d`, `rain_3d`, `rain_7d`, `rain_14d` | Rain totals over the window ending on D, D included. Same as `api/predictor.py`, checked to match on every day. |
| `month`, `day_of_year` | Calendar |
| `complaints_lag{k}` (optional) | Complaints k days before D |

- **Rain on D:** in training it is rain that fell. Live it is a forecast. We score on real rain here; Person 1's forecast-error test measures how much worse forecasts make it.
- **Complaint lag:** today's 311 count is incomplete when the forecast is made, so the newest complete count is 2 days before tomorrow and 3 days before the day after. `k = 2` matches `complaints_yesterday` in Dataset D (tomorrow only). `k = 3` is valid for both forecast days. The tool refuses `k < 2`. A model using a lag needs live 311 counts in the API (Person 5).
- **`is_spike` is never an input.** It is used only to split the error into normal and flood days.

## Train/test split

By calendar year, expanding window. To test year Y, train on every day before Jan 1 of Y (from 2019-03-01).

| Test year | Trains on | Notes |
|---|---|---|
| 2020 | 2019 | 2019 is training only |
| 2021–2025 | 2019 through Y−1 | |
| 2026 | 2019–2025 | Partial: data ends 2026-10-20 |

2024's only flood is one day at 101 complaints, so its catch rate is either 0/1 or 1/1. Don't read much into 2024 alone.

## Scores

**Error on counts.** RMSE and MAE over all test days, plus MAE on normal days (`is_spike = 0`) and flood days (`is_spike = 1`) separately. The big 2023 and 2025 floods dominate the overall RMSE, so look at the split.

**Flood catch.** A day is *flagged* when the predicted count is at or above the flag cutoff (default 100, the same cutoff that defines a flood day, `FLOOD_CUTOFF` in `src/data/flood_events.py`). A flood event is *caught* if any day within 1 day of its peak is flagged. Big (peak 500+) and small events are counted separately. The event table also shows each event's highest prediction near the peak and near the start, so "predicted 80 on a 600 day" (close) is visible next to "predicted 10" (missed).

**Onset catch (seen coming).** An event's onset is caught if any day within 1 day of its *first* flood day (`start_date`) is flagged. This is the stricter test and the one that matters for staffing ahead of a storm. It also closes a loophole: a model with a complaint lag can flag the day after a peak by echoing the count from 2–3 days earlier, which "catches" the event without forecasting it. On the day after the first flood day, a lag of 2 or more only sees counts from before the event began, so echoing can't pass the onset test. For single-day events, onset and peak are the same day. Columns: `onset`, `big_onset`, `small_onset`.

**Which events count.** From `data/labels/flood_events.csv`: events marked `yes` or `unsure` are scored, `no` is left out. `--yes-only` / `include_unsure=False` scores only `yes`.

**False alarms.** A flagged day that isn't within 1 day of any event in the list (including events marked `no`). Flagged days at most 2 days apart are grouped into one episode, using the same merge rule as flood events. We report episodes per year, not days.

**Baseline.** `SeasonalMedian`: the median training complaint count for the target day's month. Every model should beat it on error. It never flags a flood, by design.

## Open questions

1. **Flag cutoff.** Models that predict averages tend to undershoot spikes. The cutoff is a setting (`threshold=`); we may report a lower cutoff alongside 100 if it gives a fairer picture.
