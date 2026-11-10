import datetime as dt
import statistics
from typing import Dict

from api.data import DailyTable

RAIN_3D_BINS = (0.0, 0.25, 0.5, 1.0, 2.0, 3.0)


def rain_features(day: dt.date, rain: Dict[dt.date, float]) -> dict:

    def total(n: int) -> float:
        return round(sum(rain.get(day - dt.timedelta(k), 0.0) for k in range(n)), 4)

    return {
        "rain_1d": total(1),
        "rain_3d": total(3),
        "rain_7d": total(7),
        "rain_14d": total(14),
        "month": day.month,
        "day_of_year": day.timetuple().tm_yday,
    }


def rain_bin(rain_3d: float) -> int:
    i = 0
    for k, lower in enumerate(RAIN_3D_BINS):
        if rain_3d >= lower:
            i = k
    return i


class StubPredictor:

    name = "stub: seasonal normal + typical jump for this much 3-day rain (placeholder)"
    is_model = False

    def __init__(self, table: DailyTable):
        self.table = table
        by_bin = {i: [] for i in range(len(RAIN_3D_BINS))}
        for d in table.dates:
            r3 = sum(table.rain.get(d - dt.timedelta(k), 0.0) for k in range(3))
            by_bin[rain_bin(r3)].append(table.complaints[d])

        medians, last = [], 0.0
        for i in range(len(RAIN_3D_BINS)):
            # An empty bin borrows the bin below; more rain never predicts fewer calls.
            m = float(statistics.median(by_bin[i])) if by_bin[i] else last
            last = max(m, last)
            medians.append(last)
        self.uplift = [round(m - medians[0], 1) for m in medians]

    def predict(self, features: dict) -> float:
        baseline = self.table.baseline_by_month[features["month"]]
        return baseline + self.uplift[rain_bin(features["rain_3d"])]


def load_predictor(table: DailyTable):
    return StubPredictor(table)
