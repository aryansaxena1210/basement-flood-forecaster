from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

#Real daily table from Person 2 (docs/data_contract.md). Until it is merged into this
#branch, the API falls back to the fake sample and /health reports data_is_sample = true.
DAILY_CSV = REPO_ROOT / "data" / "processed" / "daily.csv"
SAMPLE_CSV = REPO_ROOT / "data" / "sample" / "daily_sample.csv"

TIMEZONE = "America/Chicago"

#Forecast shape
HORIZON_DAYS = 2  #decision 1: tomorrow and the day after
RAIN_WINDOW_DAYS = 14  #decision 2: the longest rain window the model looks at

HISTORY_DEFAULT_DAYS = 90
HISTORY_MAX_DAYS = 3000  #the whole real file is about 2,800 days

#Dollar assumptions PLACEHOLDERS
#Every dollar field in /forecast is extra_calls x one of these.
REVENUE_PER_CALL_USD = 300.0
OVERTIME_COST_PER_CALL_USD = 120.0

#Risk level, decided from predicted_calls: PLACEHOLDERS
try:
    from src.data.flood_events import FLOOD_CUTOFF as HIGH_RISK_CALLS
except ImportError:
    HIGH_RISK_CALLS = 100
#A normal day is about 8. 30+ is roughly the busiest 6% of non-flood days in daily.csv.
MEDIUM_RISK_CALLS = 30

#Browser access
CORS_ORIGINS = ["*"]
