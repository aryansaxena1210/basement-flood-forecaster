import datetime as dt
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

RiskLevel = Literal["low", "medium", "high"]


class HorizonDay(BaseModel):
    date: dt.date
    prcp_in: Optional[float] = Field(
        None, description="Rain used for this day, in inches. null when it is unknown and 0 was assumed."
    )
    predicted_calls: float = Field(..., description="Predicted complaints that day. Never negative.")
    baseline_calls: float = Field(..., description="A normal day for this time of year.")
    extra_calls: float = Field(..., description="predicted_calls - baseline_calls, never below 0.")
    spike_probability: Optional[float] = Field(
        None, description="Chance the day is a flood day. null: no planned model gives a probability yet."
    )
    risk_level: RiskLevel
    revenue_if_staffed_usd: float = Field(..., description="extra_calls x revenue_per_call_usd")
    overtime_cost_if_unstaffed_usd: float = Field(..., description="extra_calls x overtime_cost_per_call_usd")


class Assumptions(BaseModel):
    revenue_per_call_usd: float
    overtime_cost_per_call_usd: float


class ForecastResponse(BaseModel):
    generated_at: dt.datetime
    model: str = Field(..., description="What made the numbers. Starts with 'stub' until a real model is loaded.")
    horizon: List[HorizonDay]
    assumptions: Assumptions


class HistoryDay(BaseModel):
    date: dt.date
    actual_calls: int
    predicted_calls: Optional[float]
    prcp_in: Optional[float]
    is_spike: int = Field(..., description="1 inside a flood event. For shading charts only.")


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: Literal["ok"]
    model_loaded: bool = Field(..., description="false while the placeholder is answering")
    model: str
    last_data_refresh: dt.datetime = Field(..., description="When the API loaded the daily table")
    data_file: str
    data_is_sample: bool = Field(..., description="true means the numbers come from the fake sample")
    data_last_date: dt.date = Field(..., description="Newest day in the daily table")


class WhatIfRequest(BaseModel):
    prcp_in: float = Field(..., ge=0, le=20, description="Rain on the day, inches")
    prior_7d_prcp_in: float = Field(
        0.0, ge=0, le=40, description="Total rain over the 7 days before, inches. Spread evenly over them."
    )
    date: Optional[dt.date] = Field(None, description="Day to predict. Default: tomorrow (Chicago).")
