from contextlib import asynccontextmanager
from functools import lru_cache
from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from api import settings
from api.schemas import ForecastResponse, HealthResponse, HistoryDay, HorizonDay, WhatIfRequest
from api.service import ForecastService, build_service


@lru_cache(maxsize=1)
def get_service() -> ForecastService:
    return build_service()


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_service()
    yield


app = FastAPI(
    title="Basement Flood Forecaster API",
    version="0.1.0",
    description="Expected basement-flooding complaints in Chicago for the next 2 days. "
    "Contract: docs/api_contract.md.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def index():
    return {
        "name": "Basement Flood Forecaster API",
        "docs": "/docs",
        "endpoints": ["GET /forecast", "POST /forecast/what-if", "GET /history?days=90", "GET /health"],
    }


@app.get("/health", response_model=HealthResponse)
def health():
    return get_service().health()


@app.get("/forecast", response_model=ForecastResponse)
def forecast():
    return get_service().forecast()


@app.post("/forecast/what-if", response_model=HorizonDay)
def forecast_what_if(body: WhatIfRequest):
    return get_service().what_if(body)


@app.get("/history", response_model=List[HistoryDay])
def history(days: int = Query(settings.HISTORY_DEFAULT_DAYS, ge=1, le=settings.HISTORY_MAX_DAYS)):
    return get_service().history(days)
