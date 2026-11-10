
# Rainfall and 311 Complaint Merging Strategies

## Source Data

Input: data/processed/daily.csv

The source contains one row per Chicago calendar day.

- date: Calendar date
- complaint_count: Daily basement flooding complaints
- prcp_in: Higher daily precipitation value from O'Hare or Midway
- is_spike: Complaint-based flood indicator, not a model input

## Dataset B: Daily Rainfall Lag Features

Output: data/processed/dataset_b_daily_lags.csv

Contains 2,791 daily observations.

Columns:
- date
- rainfall_today
- rainfall_1_day_ago
- rainfall_2_days_ago
- complaint_count

Purpose:
Examine relationships between daily complaints and rainfall
on the same day and previous two days.

Missing rainfall is preserved as blank.

## Dataset C1: One-Day Rainfall vs. Three-Day Complaints

Output: data/processed/dataset_c1_windows.csv

Contains 2,789 overlapping three-day windows.

- rainfall_1day_in: Rainfall on the starting date
- complaints_3days: Total complaints from the starting
  date through the following two days

Purpose:
Study whether a single day's rainfall is associated with
complaints reported over the next three days.

## Dataset C2: Three-Day Rainfall vs. Three-Day Complaints

Output: data/processed/dataset_c2_windows.csv

Contains 2,789 overlapping three-day windows.

- rainfall_3days_in: Total rainfall over three days
- complaints_3days: Total complaints over the same three days

Purpose:
Study the relationship between accumulated rainfall and
complaints during multiday periods.

## Important Limitations

1. C1 and C2 contain overlapping rolling windows,
   not independently identified heavy-rain events.
2. Complaint totals overlap between adjacent rows.
3. C2 includes observed rainfall from days after the
   starting date. This cannot be used as a predictor
   available at the starting date.
4. Future complaint counts are prediction targets,
   not information available at prediction time.
5. Dataset B's rainfall_today must only be used when
   that observation would actually be available.
6. These are experimental datasets. Predictive performance
   has not yet been evaluated.

## Reproducing the Datasets

Run from the project root:

python3 src/data/build_dataset_b.py
python3 src/data/build_dataset_c.py

Both scripts require data/processed/daily.csv.

## Next Steps

- Validate the full datasets
- Compare alternative rainfall windows
- Evaluate models using chronological train/test splits
- Coordinate feature selection and evaluation with Prince

