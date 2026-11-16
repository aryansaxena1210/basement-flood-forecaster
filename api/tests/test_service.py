"""Logic tests. They need only pydantic, not FastAPI. Run from the repo root: python -m pytest api/tests"""
import datetime as dt

import pytest
from pydantic import ValidationError

from api import settings
from api.data import load_daily
from api.predictor import StubPredictor, rain_features
from api.schemas import WhatIfRequest
from api.service import ForecastService, build_service, risk_level

NOW = dt.datetime(2026, 11, 2, 11, 0, tzinfo=dt.timezone(dt.timedelta(hours=-6)))
TOMORROW = dt.date(2026, 11, 3)


@pytest.fixture(scope="module")
def table():
    return load_daily()  # the same file the API would use: daily.csv if present, else the sample


@pytest.fixture
def service(table):
    return ForecastService(table, StubPredictor(table), clock=lambda: NOW)


def all_items(service):
    items = list(service.forecast().horizon)
    for rain in (0, 0.3, 1.5, 2.5, 4.68):
        items.append(service.what_if(WhatIfRequest(prcp_in=rain, date=dt.date(2025, 7, 15))))
    return items


def test_daily_table_follows_the_data_contract(table):
    assert table.dates == sorted(table.dates)
    assert all((b - a).days == 1 for a, b in zip(table.dates, table.dates[1:])), "gap in the daily table"
    assert set(table.baseline_by_month) == set(range(1, 13))
    assert all(v >= 0 for v in table.complaints.values())


def test_rain_windows_end_on_and_include_the_day():
    day = dt.date(2023, 7, 2)
    rain = {day: 4.0, day - dt.timedelta(days=1): 1.0, day - dt.timedelta(days=5): 2.0, day - dt.timedelta(days=20): 9.0}
    f = rain_features(day, rain)
    assert (f["rain_1d"], f["rain_3d"], f["rain_7d"], f["rain_14d"]) == (4.0, 5.0, 7.0, 7.0)
    assert (f["month"], f["day_of_year"]) == (7, 183)


def test_forecast_is_tomorrow_and_the_day_after(service):
    out = service.forecast()
    assert [h.date for h in out.horizon] == [TOMORROW, TOMORROW + dt.timedelta(days=1)]
    assert len(out.horizon) == settings.HORIZON_DAYS
    assert out.assumptions.revenue_per_call_usd == settings.REVENUE_PER_CALL_USD
    assert out.assumptions.overtime_cost_per_call_usd == settings.OVERTIME_COST_PER_CALL_USD
    assert out.model.startswith("stub")


def test_extra_calls_and_dollars_follow_the_contract(service):
    for h in all_items(service):
        assert h.predicted_calls >= 0
        assert h.extra_calls == round(max(0.0, h.predicted_calls - h.baseline_calls), 1)
        assert h.revenue_if_staffed_usd == round(h.extra_calls * settings.REVENUE_PER_CALL_USD, 2)
        assert h.overtime_cost_if_unstaffed_usd == round(h.extra_calls * settings.OVERTIME_COST_PER_CALL_USD, 2)
        assert h.risk_level == risk_level(h.predicted_calls)
        assert h.spike_probability is None


def test_risk_level_cutoffs():
    assert risk_level(0) == "low"
    assert risk_level(settings.MEDIUM_RISK_CALLS - 0.1) == "low"
    assert risk_level(settings.MEDIUM_RISK_CALLS) == "medium"
    assert risk_level(settings.HIGH_RISK_CALLS) == "high"


def test_what_if_with_no_rain_is_a_normal_day(service, table):
    day = dt.date(2025, 7, 15)
    h = service.what_if(WhatIfRequest(prcp_in=0, date=day))
    assert h.predicted_calls == round(table.baseline(day), 1)
    assert h.extra_calls == 0 and h.risk_level == "low"


def test_more_rain_never_means_fewer_calls(service):
    calls = [
        service.what_if(WhatIfRequest(prcp_in=r, date=dt.date(2025, 7, 15))).predicted_calls
        for r in (0, 0.3, 0.6, 1.5, 2.5, 4.68, 8)
    ]
    assert calls == sorted(calls)
    assert calls[-1] > calls[0]


def test_what_if_defaults_to_tomorrow_and_echoes_the_rain(service):
    h = service.what_if(WhatIfRequest(prcp_in=1.2))
    assert h.date == TOMORROW and h.prcp_in == 1.2


def test_what_if_rejects_impossible_rain():
    with pytest.raises(ValidationError):
        WhatIfRequest(prcp_in=-1)
    with pytest.raises(ValidationError):
        WhatIfRequest(prcp_in=50)


def test_forecast_uses_the_rain_forecast_when_there_is_one(table):
    dry = ForecastService(table, StubPredictor(table), clock=lambda: NOW).forecast()
    wet = ForecastService(
        table, StubPredictor(table), forecast_source=lambda days: {d: 5.0 for d in days}, clock=lambda: NOW
    ).forecast()
    assert [h.prcp_in for h in wet.horizon] == [5.0, 5.0]
    assert wet.horizon[0].predicted_calls > dry.horizon[0].predicted_calls


def test_forecast_survives_a_broken_weather_feed(table):
    def broken(days):
        raise TimeoutError("api.weather.gov did not answer")

    out = ForecastService(table, StubPredictor(table), forecast_source=broken, clock=lambda: NOW).forecast()
    assert len(out.horizon) == settings.HORIZON_DAYS


def test_history_counts_back_from_the_newest_day(service, table):
    rows = service.history(30)
    assert len(rows) == 30
    assert rows[-1].date == table.last_date
    assert all((b.date - a.date).days == 1 for a, b in zip(rows, rows[1:]))
    assert all(r.actual_calls == table.complaints[r.date] for r in rows)
    assert len(service.history(10**6)) == len(table.dates)
    assert len(service.history(0)) == 1


def test_health(service, table):
    h = service.health()
    assert h.status == "ok" and h.model_loaded is False
    assert h.data_last_date == table.last_date
    assert h.data_is_sample == table.is_sample
    assert h.data_file.endswith(".csv")


def test_build_service_loads():
    assert build_service().health().status == "ok"


def test_july_2023_flood_replay_is_high_risk(service, table):
    if table.is_sample:
        pytest.skip("needs the real data/processed/daily.csv")
    # 2023-07-02: 4.68 in of rain, 1,337 complaints (docs/data_contract.md)
    h = service.what_if(WhatIfRequest(prcp_in=4.68, prior_7d_prcp_in=0.5, date=dt.date(2023, 7, 2)))
    assert h.risk_level == "high"
