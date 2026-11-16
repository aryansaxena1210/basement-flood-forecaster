import csv
import datetime as dt
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from api import settings

COLUMNS = ["date", "complaint_count", "prcp_in", "is_spike"]


@dataclass
class DailyTable:
    path: Path
    is_sample: bool
    loaded_at: dt.datetime
    dates: List[dt.date]
    complaints: Dict[dt.date, int]
    rain: Dict[dt.date, float]  # days with blank rain are left out
    spike: Dict[dt.date, int]
    baseline_by_month: Dict[int, float] = field(default_factory=dict)

    @property
    def first_date(self) -> dt.date:
        return self.dates[0]

    @property
    def last_date(self) -> dt.date:
        return self.dates[-1]

    def baseline(self, day: dt.date) -> float:
        return self.baseline_by_month[day.month]

    def rain_on(self, day: dt.date) -> Optional[float]:
        return self.rain.get(day)

    def relative_path(self) -> str:
        try:
            return self.path.resolve().relative_to(settings.REPO_ROOT).as_posix()
        except ValueError:
            return str(self.path)


def default_path() -> Path:
    return settings.DAILY_CSV if settings.DAILY_CSV.exists() else settings.SAMPLE_CSV


def load_daily(path: Optional[Path] = None, now: Optional[dt.datetime] = None) -> DailyTable:
    path = Path(path) if path else default_path()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"{path}: columns {reader.fieldnames}, expected {COLUMNS} (docs/data_contract.md)")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path} has no rows")

    dates, complaints, rain, spike = [], {}, {}, {}
    for r in rows:
        d = dt.date.fromisoformat(r["date"])
        dates.append(d)
        complaints[d] = int(r["complaint_count"])
        if r["prcp_in"].strip() != "":
            rain[d] = float(r["prcp_in"])
        spike[d] = int(r["is_spike"])
    dates.sort()

    by_month = {}
    for m in range(1, 13):
        normal = [complaints[d] for d in dates if d.month == m and not spike[d]]
        by_month[m] = float(statistics.median(normal)) if normal else 0.0

    return DailyTable(
        path=path,
        is_sample=path.resolve() == settings.SAMPLE_CSV.resolve(),
        loaded_at=now or dt.datetime.now(dt.timezone.utc),
        dates=dates,
        complaints=complaints,
        rain=rain,
        spike=spike,
        baseline_by_month=by_month,
    )
