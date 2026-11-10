# API Contract (v1)

The idea is that person 5 builds it, and person 6 consumes it. I (person 5) just wrote this without the help of a person 6, so if we decide on who person 6 will be, this is subject to change; whoever takes the dashboard should review it, and the change list at the bottom shows every place it differs from the first draft.

JSON over HTTP, FastAPI, base path `/`. Run steps: [`api/README.md`](../api/README.md). Live, clickable version of this file: http://127.0.0.1:8000/docs. The shapes are enforced by `api/schemas.py`, so change that file and this one together.

Until a real model is loaded, every endpoint answers in exactly these shapes with placeholder numbers. `/health` says which (`model_loaded`, `data_is_sample`).

**General rules**
- Dates are Chicago calendar dates, `YYYY-MM-DD`. Timestamps are ISO 8601 with the Chicago offset.
- "Calls" means Chicago 311 `Water in Basement Complaint` requests, duplicates removed (`docs/data_contract.md`). The dollar fields treat them as calls a basement-flooding business would get.
- `null` means "don't know", never 0.

## GET /forecast

Expected complaints for tomorrow and the day after.

```json
{
  "generated_at": "2026-11-02T11:00:00-06:00",
  "model": "stub: seasonal normal + typical jump for this much 3-day rain (placeholder)",
  "horizon": [
    {
      "date": "2026-11-03",
      "prcp_in": 2.5,
      "predicted_calls": 57.0,
      "baseline_calls": 6.0,
      "extra_calls": 51.0,
      "spike_probability": null,
      "risk_level": "medium",
      "revenue_if_staffed_usd": 15300.0,
      "overtime_cost_if_unstaffed_usd": 6120.0
    },
    {
      "date": "2026-11-04",
      "prcp_in": null,
      "predicted_calls": 6.0,
      "baseline_calls": 6.0,
      "extra_calls": 0.0,
      "spike_probability": null,
      "risk_level": "low",
      "revenue_if_staffed_usd": 0.0,
      "overtime_cost_if_unstaffed_usd": 0.0
    }
  ],
  "assumptions": {
    "revenue_per_call_usd": 300.0,
    "overtime_cost_per_call_usd": 120.0
  },
  "notes": [
    "No rain forecast for 2026-11-04, so 0 in was assumed. ..."
  ]
}
```

| Field | Meaning |
|---|---|
| `model` | What made the numbers. Starts with `stub` while the placeholder answers. |
| `horizon` | Always 2 entries: tomorrow, then the day after (Chicago time). |
| `prcp_in` | Rain used for that day, inches. `null` when no forecast was available and 0 was assumed. |
| `predicted_calls` | Predicted complaints that day, never negative. |
| `baseline_calls` | A normal day for this time of year (TASKS.md decision 1). For now: median complaints on non-flood days in the same month. |
| `extra_calls` | `predicted_calls - baseline_calls`, never below 0. |
| `spike_probability` | Always `null` for now. Every planned model predicts a count, not a probability. Filled only if someone adds a flood/no-flood classifier. |
| `risk_level` | From `predicted_calls`: `high` at 100+ (the flood-day cutoff in `docs/flood_events.md`), `medium` at 30+, else `low`. Cutoffs live in `api/settings.py`. |
| `revenue_if_staffed_usd` | `extra_calls x revenue_per_call_usd` |
| `overtime_cost_if_unstaffed_usd` | `extra_calls x overtime_cost_per_call_usd` |
| `assumptions` | The dollar rates used. **Placeholders** until the team agrees on them (`api/settings.py`). |
| `notes` | Plain-English caveats to show next to the numbers: fake sample data in use, no rain forecast, rain assumed dry, weather feed failed. Empty list when there's nothing to say. |

## POST /forecast/what-if

Type in the rain yourself. This is the fallback when the National Weather Service forecast has no rain amounts (TASKS.md ground rules), and it's the demo tool, since a real storm on demo day is unlikely.

Body (only `prcp_in` is required):

```json
{ "prcp_in": 4.68, "prior_7d_prcp_in": 0.5, "date": "2023-07-02" }
```

| Field | Meaning |
|---|---|
| `prcp_in` | Rain on the day, inches, 0 to 20. |
| `prior_7d_prcp_in` | Total rain over the 7 days before, inches, 0 to 40. Spread evenly over those days. Default 0. |
| `date` | Day to predict. Default: tomorrow. A past date replays it (the month sets the normal day). |

Days 8 to 14 before are taken as dry, and real recent rain is not used, so the same body always gives the same answer.

Returns one object shaped exactly like a `horizon` item. Bad input (negative rain, missing `prcp_in`) returns HTTP 422.

## GET /history?days=90

Past days for the dashboard chart, oldest first. `days` is 1 to 3000, default 90.

```json
[
  {
    "date": "2026-10-20",
    "actual_calls": 3,
    "predicted_calls": 6.0,
    "prcp_in": 0.0,
    "is_spike": 0
  }
]
```

- Counts back from the **newest day in `daily.csv`**, not from today. `daily.csv` is a committed snapshot that ends a few days back (currently 2026-10-20).
- `actual_calls` is `complaint_count` from `daily.csv`. `prcp_in` is `null` if rain was blank that day.
- `predicted_calls` is what the current model (or placeholder) says for that day using the rain that actually fell. These are in-sample until Person 4 provides out-of-sample predictions, so don't present them as a score.
- `is_spike` is 1 inside a flood event. For shading the chart only.

## GET /health

```json
{
  "status": "ok",
  "model_loaded": false,
  "model": "stub: seasonal normal + typical jump for this much 3-day rain (placeholder)",
  "last_data_refresh": "2026-11-02T11:51:01-06:00",
  "data_file": "data/processed/daily.csv",
  "data_is_sample": false,
  "data_last_date": "2026-10-20"
}
```

| Field | Meaning |
|---|---|
| `model_loaded` | `false` while the placeholder answers. |
| `last_data_refresh` | When the API loaded the daily table (at startup). |
| `data_file` | Which file it loaded. |
| `data_is_sample` | `true` means the fake `data/sample/daily_sample.csv`: never quote those numbers. |
| `data_last_date` | Newest day in that file. |

## Changes from the first draft

1. **Fixed the example dollars.** 73 x 120 is 8,760, not 8,800.
2. **`spike_probability` is `null` for now.** None of the planned models (seasonal, Lasso, Ridge, XGBoost, LightGBM) gives a probability.
3. **`risk_level` now has a rule:** `high` = 100+ predicted (the flood-day cutoff), `medium` = 30+, else `low`.
4. **`extra_calls` can't go negative**, and neither can `predicted_calls` (Lasso and Ridge can predict below 0).
5. **Added to `/forecast`:** `model`, `notes`, and `prcp_in` in each `horizon` item, so the dashboard can show what rain went in and say when something is a guess.
6. **`/forecast/what-if` is no longer optional** and takes an optional `date`. The planned model inputs include month and day of year, so the date matters.
7. **Added `is_spike` to `/history`** for shading flood days, and defined where "last 90 days" counts from.
8. **`/health`:** defined `last_data_refresh` and added `model`, `data_file`, `data_is_sample`, `data_last_date`.
9. **Timestamps carry the Chicago offset**, so "tomorrow" is never the server's UTC tomorrow.
