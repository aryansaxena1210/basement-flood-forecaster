# Team Plan: 6 People, 4 Weeks

**The project in one line:** turn a rain forecast into "expect about N extra basement-flooding complaints in the next 1-2 days," using Chicago 311 complaints and rain data.

**Due: Tuesday, Dec 1.** Work runs Oct 26 to Nov 20. Thanksgiving week (Nov 23-27) is buffer, and Nov 30 is for final checks. The dashboard is a nice-to-have.

Where the data comes from, with working example calls: [`data_sources.md`](data_sources.md). Until real files exist, use `data/sample/daily_sample.csv` (fake, never quote results from it).

## Who does what

| # | Role | Owns | Check-buddy |
|---|---|---|---|
| 1 | Weather data (NOAA, NWS) and checking floods against rain | `src/data` | 2 |
| 2 | 311 data, `daily.csv`, flood-event labels | `src/data` | 1 |
| 3 | Features and baseline models (seasonal, Lasso, Ridge) | `src/features`, `src/models` | 4 |
| 4 | Test harness and advanced models (XGBoost, LightGBM) | `src/models` | 3 |
| 5 | Backend API | `api` | 6 |
| 6 | Dashboard, report, schedule, dollar assumptions | `dashboard`, `reports` | 5 |

A buddy reads your pull request before it's merged.

## Contracts: the docs other people build on

Each of these is a deliverable with an owner and a file path. If it isn't in the repo at that path, it isn't done. Other people code against these, so don't change one without telling them.

| Contract | File | Owner | Due | Who builds on it |
|---|---|---|---|---|
| Daily table columns | `docs/data_contract.md` (already written) | 2 | done | 3, 4 |
| Forecast function: what it takes in and what it returns | `docs/forecast_input.md` | 1 | Fri, Oct 30 | 5 |
| Flood rule (what counts as a flood) and flood list | `docs/flood_events.md`, `data/labels/flood_events.csv` | 2, checked by 1 | Fri, Oct 30 (draft), Fri, Nov 6 (final) | 3, 4 |
| Model-ready table columns | `docs/features.md` | 3 | Fri, Oct 30 | 4 |
| How the scoring works | `docs/evaluation.md` | 4 | Wed, Oct 28 | 3 |
| How to load a saved model and get a prediction | `docs/model_interface.md` | 4 | Fri, Oct 30 | 5, 1 |
| API answers | `docs/api_contract.md` (already written) | 5 | done | 6 |

## Deliverables by week

| # | Week 1 (Oct 26-30): scripts and contracts | Week 2 (Nov 2-6): real data, first model | Week 3 (Nov 9-13): improve, then freeze | Week 4 (Nov 16-20): report and practice |
|---|---|---|---|---|
| 1 | Script that downloads daily rain for O'Hare and Midway: `src/data/fetch_noaa.py`, saves to `data/raw`. Function that gets the rain forecast for the next 3 days in inches: `src/data/forecast.py`. Contract: `docs/forecast_input.md`. | Check each big flood against rain records and news stories (including July 2022). Write what you found in the notes column of `data/labels/flood_events.csv`. Add a function for the last few days of real rain to `src/data/forecast.py`. | Hook the forecast function into the API so `/forecast` uses today's real forecast. Forecast-error test: add random error to the rain going into Person 4's saved model and see how much predictions get worse. Results in `reports/forecast_error_test.md`. | Weather section: `reports/weather.md`. |
| 2 | Script that downloads daily complaint counts, leaves out duplicates, puts 0 on days with none: `src/data/fetch_311.py`. Script that joins complaints with rain: `src/data/build_daily.py`, output `data/processed/daily.csv` (rough version by **Wed**). Flood rule: `docs/flood_events.md`. First flood list: `data/labels/flood_events.csv`. How you cleaned the data: `docs/data_cleaning.md`. | `daily.csv` v1 finished and shared with the team (link in the README). Write up the noise in the data, meaning complaints that weren't caused by rain: `docs/label_noise.md`. | Fix data problems other people find. Polish the dashboard on the live API if it exists. | Data and flood-labels section: `reports/data_labels.md`. |
| 3 | Contract: `docs/features.md` listing the model inputs (rain over the last 1, 3, 7, 14 days, month, day of year). Script that builds them: `src/features/build_features.py`, working on the sample data. **Discuss feature shape with everyone in a meeting** | Build `data/processed/features.csv` from the real data. Simple models (usual-for-this-time-of-year, Lasso, Ridge) in `src/models/baselines.py`, scored with Person 4's scoring tool. | Find which inputs matter most and compare with the Chicago study (R = 0.74 street, 0.37 basement): `reports/feature_importance.md`. Final simple-model scores table: `reports/baseline_scores.md`. | Simple-models section: `reports/baselines.md`. |
| 4 | Scoring tool `src/models/evaluate.py`: train on earlier years, test on the next, report the average error, check whether each real flood was caught, and score big and small floods separately. Contract: `docs/evaluation.md` (by **Wed**). Contract: `docs/model_interface.md`. | First XGBoost and LightGBM models in `src/models/boosted.py`, scored next to the simple ones. Save a model in `models/` following `docs/model_interface.md`. | Tune the models. Save the best one as `models/best_model` early in the week, because Person 1 needs it. | Model results section: `reports/models.md`. |
| 5 | The API in `api/`, returning made-up answers in the format of `docs/api_contract.md`. Run steps in `api/README.md`. | Plug the simple model into the API by **Wed**. Add `/history`. Put the dollar amounts in `api/settings.py` as labeled settings, agreed with Person 6. | Plug in the best model and build its inputs from live data. Basic tests in `api/tests/`. | Fix bugs. Demo script `scripts/demo.py` that runs cleanly three times in a row. |
| 6 | Grading info added to the root `README.md` (due date is Dec 1). Set up the chat channel, check-in times, and task board (link in the README). Report outline: `reports/outline.md`. Dashboard sketch in `dashboard/` (nice-to-have). | Early results into the report draft: `reports/final_report.md`. Dashboard page showing the forecast and recent history in `dashboard/` (nice-to-have). | Pull the report sections together into `reports/final_report.md`. | Limitations section: `reports/limitations.md`. Finish `reports/final_report.md`. |

Everyone in week 4: rehearse the demo twice. Thanksgiving week is buffer, so anything that slipped lands there, not past Dec 1.

## Milestones

| When | What |
|---|---|
| Wed, Oct 28 | Rough `daily.csv` with real data (Persons 1 + 2). `docs/evaluation.md` written (Person 4). |
| Fri, Oct 30 | All week 1 contracts in the table above are in the repo. Scoring tool runs on the sample data. |
| Wed, Nov 4 | **First end-to-end run:** simple model, real data, through the API (Persons 3, 5). Basic dashboard on top if Person 6 has it. |
| Fri, Nov 6 | `daily.csv` v1 finished, flood list final |
| Fri, Nov 13 | **Code freeze.** Best model in the API. Bug fixes only after this. |
| Fri, Nov 20 | Final report drafted, demo rehearsed twice |
| Nov 23-27 | Buffer (Thanksgiving week) |
| Mon, Nov 30 | Final read-through and submission check |
| **Tue, Dec 1** | **Due** |

## Decisions already made

1. **What we predict:** the daily complaint count (duplicates removed) for tomorrow and the day after. "Extra calls" is predicted count minus a normal day for that time of year.
2. **Rain inputs:** the larger of O'Hare and Midway (whichever has data if the other is blank), plus rain over the last 1, 3, 7, and 14 days.
3. **How we test:** by year. Train on earlier years, test on the next. Every year from 2019 on has at least one flood-sized spike, so every test year has something to catch. 2019 is training only, and 2018 has about a week of data, so we skip it.
4. **How we score floods:** did we flag each real flood within a day, how many false alarms per year, and RMSE/MAE. Big and small floods are scored separately, because the huge 2023 and 2025 floods would otherwise swamp the average.
5. **Forecast vs. real rain:** we train on rain that fell, but the live tool uses forecasts, which are less exact. The report says so, and one test adds forecast-sized errors.
6. **`is_spike` is for scoring only.** It is never a model input.

## Ground rules

- Stuck for a day? Say so in the chat. Most blocks here are waiting on a teammate's file.
- One branch per person (`p1-weather`, `p2-311`, ...). Pull request into `main`. Your buddy reads it first.
- Python 3.11 or 3.12.
- Raw data isn't in git. Scripts in `src/data` must recreate it. The finished `daily.csv` and the event list in `data/labels` are in git, so a pull gets them.
- The dashboard is a nice-to-have. If it slips, cut it to one plain chart or drop it. The API and the model are the product.
- If the NWS forecast has no usable rain amounts when a storm is forecast, use `POST /forecast/what-if` and type in the rainfall.
