import datetime as dt
from typing import Callable, Dict, List

from api import settings
from api.data import DailyTable, load_daily
from api.predictor import load_predictor, rain_features
from api.schemas import (
    Assumptions,
    ForecastResponse,
    HealthResponse,
    HistoryDay,
    HorizonDay,
    WhatIfRequest,
)

try:
    from zoneinfo import ZoneInfo

    CHICAGO = ZoneInfo(settings.TIMEZONE)
except Exception:
    CHICAGO = None

ForecastSource = Callable[[List[dt.date]], Dict[dt.date, float]]


def no_rain_forecast(days: List[dt.date]) -> Dict[dt.date, float]:
    return {}


def chicago_now() -> dt.datetime:
    if CHICAGO is None:
        return dt.datetime.now().astimezone()
    return dt.datetime.now(CHICAGO)


def risk_level(predicted_calls: float) -> str:
    if predicted_calls >= settings.HIGH_RISK_CALLS:
        return "high"
    if predicted_calls >= settings.MEDIUM_RISK_CALLS:
        return "medium"
    return "low"


class ForecastService:
    def __init__(
        self,
        table: DailyTable,
        predictor,
        forecast_source: ForecastSource = no_rain_forecast,
        clock: Callable[[], dt.datetime] = chicago_now,
    ):
        self.table = table
        self.predictor = predictor
        self.forecast_source = forecast_source
        self.clock = clock

    #shared

    def assumptions(self) -> Assumptions:
        return Assumptions(
            revenue_per_call_usd=settings.REVENUE_PER_CALL_USD,
            overtime_cost_per_call_usd=settings.OVERTIME_COST_PER_CALL_USD,
        )

    def horizon_dates(self) -> List[dt.date]:
        tomorrow = self.clock().date() + dt.timedelta(days=1)
        return [tomorrow + dt.timedelta(days=k) for k in range(settings.HORIZON_DAYS)]

    def predict_day(self, day: dt.date, rain: Dict[dt.date, float]) -> HorizonDay:
        predicted = round(max(0.0, float(self.predictor.predict(rain_features(day, rain)))), 1)
        baseline = round(self.table.baseline(day), 1)
        extra = round(max(0.0, predicted - baseline), 1)
        return HorizonDay(
            date=day,
            prcp_in=rain.get(day),
            predicted_calls=predicted,
            baseline_calls=baseline,
            extra_calls=extra,
            spike_probability=None,
            risk_level=risk_level(predicted),
            revenue_if_staffed_usd=round(extra * settings.REVENUE_PER_CALL_USD, 2),
            overtime_cost_if_unstaffed_usd=round(extra * settings.OVERTIME_COST_PER_CALL_USD, 2),
        )

    #endpoints

    def forecast(self) -> ForecastResponse:
        days = self.horizon_dates()
        try:
            forecast_rain = self.forecast_source(days) or {}
        except Exception:
            forecast_rain = {}

        rain = {}
        d = days[0] - dt.timedelta(days=settings.RAIN_WINDOW_DAYS - 1)
        while d <= days[-1]:
            if d in self.table.rain:
                rain[d] = self.table.rain[d]
            elif d in forecast_rain:
                rain[d] = float(forecast_rain[d])
            d += dt.timedelta(days=1)

        return ForecastResponse(
            generated_at=self.clock().replace(microsecond=0),
            model=self.predictor.name,
            horizon=[self.predict_day(day, rain) for day in days],
            assumptions=self.assumptions(),
        )

    def what_if(self, req: WhatIfRequest) -> HorizonDay:
        day = req.date or self.horizon_dates()[0]
        rain = {day: req.prcp_in}
        for k in range(1, 8):
            rain[day - dt.timedelta(days=k)] = req.prior_7d_prcp_in / 7
        return self.predict_day(day, rain)

    def history(self, days: int = settings.HISTORY_DEFAULT_DAYS) -> List[HistoryDay]:
        days = max(1, min(days, len(self.table.dates)))
        out = []
        for d in self.table.dates[-days:]:
            predicted = round(max(0.0, float(self.predictor.predict(rain_features(d, self.table.rain)))), 1)
            out.append(
                HistoryDay(
                    date=d,
                    actual_calls=self.table.complaints[d],
                    predicted_calls=predicted,
                    prcp_in=self.table.rain.get(d),
                    is_spike=self.table.spike[d],
                )
            )
        return out

    def health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            model_loaded=self.predictor.is_model,
            model=self.predictor.name,
            last_data_refresh=self.table.loaded_at.replace(microsecond=0),
            data_file=self.table.relative_path(),
            data_is_sample=self.table.is_sample,
            data_last_date=self.table.last_date,
        )


def build_service() -> ForecastService:
    table = load_daily(now=chicago_now())
    return ForecastService(table, load_predictor(table))
