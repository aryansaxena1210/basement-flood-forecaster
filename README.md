# Basement Flood Forecaster

Predicts storm-driven basement flooding demand 24-48 hours ahead from rain forecasts (Chicago 311 + NOAA).

## Setup
```
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Layout
- `data/sample/` synthetic data in the final format (committed). `data/raw` is git-ignored. `data/processed` and `data/labels` are committed.
- `src/data`, `src/features`, `src/models` pipeline code
- `notebooks/<your-folder>/` your own exploration and debugging scripts and their figures, one folder per person (e.g. `p2_311`). Don't put files in someone else's folder.
- `api/` FastAPI backend, `dashboard/` front end, `reports/` write-up
- `docs/` data contract, API contract, task board

## Workflow
- Read `docs/TASKS.md` for your row.
- One branch per person (`p1-weather`, `p2-311`, ...). Open a PR into `main`.
- Raw data is not committed; scripts in `src/data` must be able to regenerate it. `data/processed` (e.g. `daily.csv`) and `data/labels` are committed, so a pull gets them. Ofcourse, these mock-data-generation scripts are not added yet, the person working on the data layer should do this on priority to unblock others

## Data sources
Where the training and forecast data comes from, with working example calls: `docs/data_sources.md`.
