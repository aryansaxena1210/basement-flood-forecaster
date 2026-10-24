# API Contract

*THIS IS JUST AN EXAMPLE FILE (A VERY VERY VERY ROUGH DRAFT). PERSON 5 AND 6 SHOULD HOP ON A CALL AND REDO THIS FILE TOGETHER. I have given you a very rough STARTING POINT.*

Person 5 builds it, Person 6 consumes it. Until the model exists, endpoints return stub values in this exact shape.
JSON, FastAPI, base path `/`.

## GET /forecast
Predicted extra emergency calls for the next 24-48 hours.

```json
{
  "generated_at": "2026-10-23T12:00:00",
  "horizon": [
    {
      "date": "2026-10-24",
      "predicted_calls": 85.0,
      "baseline_calls": 12.0,
      "extra_calls": 73.0,
      "spike_probability": 0.82,
      "risk_level": "high",
      "revenue_if_staffed_usd": 21900.0,
      "overtime_cost_if_unstaffed_usd": 8800.0
    }
  ],
  "assumptions": {
    "revenue_per_call_usd": 300.0,
    "overtime_cost_per_call_usd": 120.0
  }
}
```

- `risk_level`: one of `low`, `medium`, `high`.
- `horizon` has 2 entries (next 2 days).
- Dollar fields = `extra_calls` x the matching value in `assumptions`. The rates are placeholders until the team agrees on them.

## GET /history
Past days for the dashboard chart. Optional query `?days=90` (default 90).

```json
[
  {
    "date": "2026-07-26",
    "actual_calls": 640,
    "predicted_calls": 590.0,
    "prcp_in": 5.8
  }
]
```

## GET /health
```json
{ "status": "ok", "model_loaded": true, "last_data_refresh": "2026-10-23T06:00:00" }
```

## POST /forecast/what-if (optional)
Body: `{ "prcp_in": 4.0, "prior_7d_prcp_in": 1.5 }`. Returns one entry shaped like a `horizon` item.
