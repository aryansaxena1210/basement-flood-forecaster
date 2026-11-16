# API (Person 5)

FastAPI backend. What each endpoint returns is in [`docs/api_contract.md`](../docs/api_contract.md).

## Run it

From the **repo root** (the code imports `api.` and `src.`, and reads `data/` from there). PowerShell:

```
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open http://127.0.0.1:8000/docs. Every endpoint has a "Try it out" button.

Quick checks from a second PowerShell window:

```
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/forecast
curl.exe "http://127.0.0.1:8000/history?days=7"
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/forecast/what-if -ContentType "application/json" -Body '{"prcp_in": 4.68, "prior_7d_prcp_in": 0.5, "date": "2023-07-02"}'
```

The last one replays the July 2, 2023 storm (4.68 in, 1,337 real complaints).

## Test it

```
python -m pytest api/tests -q
```

`test_service.py` checks the logic. `test_endpoints.py` checks the HTTP layer; it is skipped if `fastapi` or `httpx` isn't installed. One test needs the real `daily.csv` and is skipped on the sample.

## What's real and what's a placeholder

| Piece | Now | Becomes | Where to change it |
|---|---|---|---|
| Daily data | `data/processed/daily.csv` if it's there, else the **fake** `data/sample/daily_sample.csv`. `/health` shows which (`data_is_sample`), and `/forecast` warns in `notes`. | Person 2's `daily.csv` once `p2-311` is merged | `api/settings.py` |
| Prediction | `StubPredictor`: the normal count for the month plus the typical jump for that much rain over 3 days, both measured from the daily table. Not a model. | Person 3's simple model (Wed Nov 4), then Person 4's best model (week 3) | `load_predictor()` in `api/predictor.py` |
| Model inputs | `rain_features()`: rain over the last 1, 3, 7, 14 days, month, day of year | Whatever `docs/features.md` says, ideally by calling Person 3's own code | `api/predictor.py` |
| Rain forecast | None, so 0 in is assumed and `notes` says so | Person 1's `src/data/forecast.py` (`docs/forecast_input.md`) | `no_rain_forecast()` in `api/service.py` |
| Normal day (`baseline_calls`) | Median complaints on non-flood days in the same month | Person 3's seasonal baseline, so the API and report agree | `DailyTable.baseline()` in `api/data.py` |
| Dollar amounts, risk cutoffs | Placeholders | Agreed numbers | `api/settings.py` |

## Files

- `main.py`: the FastAPI app and routes. Thin on purpose.
- `service.py`: everything the endpoints answer. `predict_day()` is used by `/forecast`, `/forecast/what-if` and `/history`, so a new model changes all three.
- `predictor.py`: the model goes here.
- `data.py`: loads the daily table once.
- `schemas.py`: response shapes. They are the contract in code; change `docs/api_contract.md` with them.
- `settings.py`: every number someone might want to change.
- `tests/`: `python -m pytest api/tests`.

## Plugging in a model

1. Write a class in `predictor.py` with `name` (string), `is_model = True`, and `predict(features: dict) -> float`.
2. Return it from `load_predictor()`.
3. Run the tests. `/health` should now show `model_loaded: true`.
