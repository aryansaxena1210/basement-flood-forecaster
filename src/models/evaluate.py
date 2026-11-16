"""Scoring tool: train on earlier years, test on the next. Rules: docs/evaluation.md.

Usage from code:
    from src.models.evaluate import evaluate, SeasonalMedian
    result = evaluate(SeasonalMedian, complaint_lag=None)
    result.print()

`make_model` is any zero-argument callable returning an object with
fit(X, y) and predict(X) (scikit-learn style). A fresh model is made for
every test year.

Command line (seasonal baseline):
    python -m src.models.evaluate [--lag 3] [--threshold 100] [--yes-only]
"""
import argparse
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.data.flood_events import FLOOD_CUTOFF, MERGE_GAP
from src.features.build_features import REPO_ROOT, load_daily, make_features

EVENTS_CSV = REPO_ROOT / "data" / "labels" / "flood_events.csv"
FIRST_TEST_YEAR = 2020  # 2019 is training only (TASKS.md decision 3)
CATCH_WINDOW = 1        # a flood is caught if flagged within this many days of its peak
ONSET_WINDOW = 1        # ...and seen coming if flagged within this many days of its first flood day
ALARM_MARGIN = 1        # flags this close to any event are not false alarms


def load_events(path=EVENTS_CSV):
    e = pd.read_csv(path, parse_dates=["start_date", "end_date", "peak_date"])
    e["confirmed"] = e["confirmed"].fillna("").astype(str).str.strip().str.lower()
    e["big"] = e["big"].astype(str).str.strip().str.lower().eq("yes")
    return e


class SeasonalMedian:
    """Normal day for the time of year: median training complaints for the target's month."""

    def fit(self, X, y):
        self.by_month_ = y.groupby(X["month"].values).median()
        self.overall_ = float(y.median())
        return self

    def predict(self, X):
        return X["month"].map(self.by_month_).fillna(self.overall_).to_numpy(float)


def _rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2))) if len(a) else np.nan


def _mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b)))) if len(a) else np.nan


def _episodes(days):
    """Group sorted days into runs where neighbours are at most MERGE_GAP days apart."""
    runs = []
    for d in days:
        if runs and (d - runs[-1][-1]).days <= MERGE_GAP:
            runs[-1].append(d)
        else:
            runs.append([d])
    return runs


@dataclass
class Result:
    name: str
    predictions: pd.DataFrame  # date -> actual, predicted, is_spike, flagged, year
    per_year: pd.DataFrame     # one row per test year, plus "all"
    events: pd.DataFrame       # one row per scored flood event
    false_alarms: pd.DataFrame # one row per false-alarm episode
    threshold: float

    def print(self):
        print(f"== {self.name}  (flag at predicted >= {self.threshold:g})")
        print(self.per_year.round(1).to_string())
        print()
        print(self.events.round(0).to_string(index=False))
        print()


def evaluate(make_model, complaint_lag=None, threshold=FLOOD_CUTOFF, test_years=None,
             include_unsure=True, name=None, daily=None, events=None):
    daily = load_daily() if daily is None else daily
    events = load_events() if events is None else events

    X = make_features(daily, complaint_lag)
    y = daily["complaint_count"].astype(float)
    usable = X.notna().all(axis=1)
    X, y = X[usable], y[usable]
    years = X.index.year
    if test_years is None:
        test_years = range(FIRST_TEST_YEAR, int(years.max()) + 1)

    preds = []
    for yr in test_years:
        train, test = years < yr, years == yr
        if not test.any() or not train.any():
            continue
        model = make_model()
        model.fit(X[train], y[train])
        preds.append(pd.Series(np.asarray(model.predict(X[test]), dtype=float), index=X.index[test]))
    pred = pd.concat(preds)

    t = pd.DataFrame({
        "actual": y.loc[pred.index],
        "predicted": pred,
        "is_spike": daily.loc[pred.index, "is_spike"].astype(int),
    })
    t["flagged"] = t["predicted"] >= threshold
    t["year"] = t.index.year
    tested_years = sorted(t["year"].unique())

    # Flood events: catch rate. Events marked "no" are not scored.
    keep = events["confirmed"].ne("no")
    if not include_unsure:
        keep &= events["confirmed"].eq("yes")
    scored = events[keep & events["peak_date"].dt.year.isin(tested_years)]
    rows = []
    for _, ev in scored.iterrows():
        near = t.loc[ev.peak_date - pd.Timedelta(days=CATCH_WINDOW): ev.peak_date + pd.Timedelta(days=CATCH_WINDOW)]
        onset = t.loc[ev.start_date - pd.Timedelta(days=ONSET_WINDOW): ev.start_date + pd.Timedelta(days=ONSET_WINDOW)]
        during = t.loc[ev.start_date: ev.end_date]
        rows.append({
            "event_id": ev.event_id, "peak_date": ev.peak_date.date(), "year": ev.peak_date.year,
            "big": ev.big, "confirmed": ev.confirmed or "-", "peak_count": ev.peak_count,
            "max_pred_near_peak": near["predicted"].max(),
            "max_pred_near_start": onset["predicted"].max(),
            "event_mae": _mae(during["actual"], during["predicted"]),
            "caught": bool(near["flagged"].any()),
            "onset": bool(onset["flagged"].any()),
        })
    ev_table = pd.DataFrame(rows)

    # False alarms: flagged days not within ALARM_MARGIN of any event (scored or not).
    near_event = pd.Series(False, index=t.index)
    for _, ev in events.iterrows():
        near_event.loc[ev.start_date - pd.Timedelta(days=ALARM_MARGIN): ev.end_date + pd.Timedelta(days=ALARM_MARGIN)] = True
    alarm_days = list(t.index[t["flagged"] & ~near_event])
    fa = pd.DataFrame([{"start": r[0].date(), "end": r[-1].date(), "year": r[0].year, "days": len(r),
                        "max_pred": t.loc[r, "predicted"].max(), "max_actual": t.loc[r, "actual"].max()}
                       for r in _episodes(alarm_days)],
                      columns=["start", "end", "year", "days", "max_pred", "max_actual"])

    def summarise(tt, ee, ff):
        normal, flood = tt[tt.is_spike == 0], tt[tt.is_spike == 1]
        big = ee[ee["big"]] if len(ee) else ee
        small = ee[~ee["big"]] if len(ee) else ee
        return {
            "days": len(tt),
            "rmse": _rmse(tt.actual, tt.predicted), "mae": _mae(tt.actual, tt.predicted),
            "mae_normal": _mae(normal.actual, normal.predicted),
            "mae_flood": _mae(flood.actual, flood.predicted),
            "floods": len(ee), "caught": int(ee["caught"].sum()) if len(ee) else 0,
            "big": len(big), "big_caught": int(big["caught"].sum()) if len(big) else 0,
            "small": len(small), "small_caught": int(small["caught"].sum()) if len(small) else 0,
            "onset": int(ee["onset"].sum()) if len(ee) else 0,
            "big_onset": int(big["onset"].sum()) if len(big) else 0,
            "small_onset": int(small["onset"].sum()) if len(small) else 0,
            "false_alarms": len(ff),
        }

    per_year = {}
    for yr in tested_years:
        per_year[yr] = summarise(t[t.year == yr],
                                 ev_table[ev_table.year == yr] if len(ev_table) else ev_table,
                                 fa[fa.year == yr])
    per_year["all"] = summarise(t, ev_table, fa)
    per_year = pd.DataFrame(per_year).T
    counts = ["days", "floods", "caught", "big", "big_caught", "small", "small_caught",
              "onset", "big_onset", "small_onset", "false_alarms"]
    per_year = per_year.astype({c: int for c in counts} | {c: float for c in per_year.columns if c not in counts})

    label = name or getattr(make_model, "__name__", str(make_model))
    label += f" | lag={complaint_lag}" + ("" if include_unsure else " | yes-only")
    return Result(label, t, per_year, ev_table, fa, threshold)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lag", type=int, default=None, help="add complaints from LAG days before the target (>= 2)")
    ap.add_argument("--threshold", type=float, default=FLOOD_CUTOFF)
    ap.add_argument("--yes-only", action="store_true", help="score only events confirmed 'yes'")
    a = ap.parse_args()
    evaluate(SeasonalMedian, complaint_lag=a.lag, threshold=a.threshold,
             include_unsure=not a.yes_only).print()


if __name__ == "__main__":
    main()
