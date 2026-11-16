"""Model inputs built from data/processed/daily.csv.

One row per target day D. Every column only uses information that is known
when the forecast for D is made (see docs/evaluation.md):

- rain_1d, rain_3d, rain_7d, rain_14d: rain totals over the window ending on D,
  D included. In training this is rain that fell; live, D's rain is the forecast.
  Same definition as api/predictor.py:rain_features (blank rain counts as 0).
- month, day_of_year: calendar.
- complaints_lag{k} (optional): complaint count k days before D. Use k >= 2
  for tomorrow's forecast and k >= 3 for the day after, because today's 311
  count is still incomplete when the forecast is made.

is_spike is never an input.
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DAILY_CSV = REPO_ROOT / "data" / "processed" / "daily.csv"

RAIN_WINDOWS = (1, 3, 7, 14)


def load_daily(path=DAILY_CSV):
    """daily.csv as a DataFrame indexed by date, sorted, no gaps."""
    daily = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    full = pd.date_range(daily.index[0], daily.index[-1], freq="D")
    if len(full) != len(daily):
        raise ValueError(f"{path} has gaps: {len(full) - len(daily)} missing days")
    return daily


def make_features(daily, complaint_lag=None):
    """Return the model input table (index = target date).

    complaint_lag: None for rain + calendar only, or an int k (or list of ints)
    to add complaints_lag{k} columns. Rows whose lag reaches before the first
    day of data are NaN in those columns.
    """
    rain = daily["prcp_in"].fillna(0.0)
    X = pd.DataFrame(index=daily.index)
    for n in RAIN_WINDOWS:
        X[f"rain_{n}d"] = rain.rolling(n, min_periods=1).sum().round(4)
    X["month"] = daily.index.month
    X["day_of_year"] = daily.index.dayofyear

    if complaint_lag is not None:
        lags = [complaint_lag] if isinstance(complaint_lag, int) else list(complaint_lag)
        for k in lags:
            if k < 2:
                raise ValueError("complaint lag must be >= 2: today's count is incomplete at forecast time")
            X[f"complaints_lag{k}"] = daily["complaint_count"].shift(k)
    return X


if __name__ == "__main__":
    X = make_features(load_daily(), complaint_lag=3)
    print(X.tail())
    print(len(X), "rows")
