# NWS Rainfall Forecast Input

## Overview
The `src/data/forecast.py` script retrieves short-term precipitation forecasts from the National Weather Service (NWS) for Chicago O'Hare.

It converts precipitation from millimeters to inches and calculates daily rainfall totals for today and the following two calendar days.

## Data Source
- Provider: National Weather Service (NWS)
- API endpoint: https://api.weather.gov/gridpoints/LOT/66,77
- Forecast grid: LOT/66,77 (Chicago O'Hare area)
- Data field: `properties.quantitativePrecipitation.values`
- Original unit: millimeters (`wmoUnit:mm`)
- Output unit: inches

## How to Run

From the project root directory:

```bash
python3 src/data/forecast.py
```

Python requires the `requests` package.

## Example Output

```text
NWS Daily Rainfall Forecast (Chicago)
-------------------------------------
2026-11-03 : 0.03 inches
2026-11-04 : 0.08 inches
2026-11-05 : 0.0 inches
```

These are example forecast values captured on November 3, 2026. Actual values change as the NWS updates its forecast.

## Processing Method
1. Request the NWS grid forecast with a User-Agent header.
2. Extract precipitation values and their forecast time intervals.
3. Convert precipitation from millimeters to inches using `inches = mm / 25.4`.
4. Convert UTC timestamps to the `America/Chicago` time zone.
5. Allocate precipitation proportionally when a forecast interval crosses local midnight.
6. Sum rainfall for each calendar date.
7. Display today's date and the next two dates.

## Limitations
- The forecast updates regularly and may change between runs.
- Today's rainfall total may represent only the remaining forecast hours, not the full day.
- The final day may have incomplete forecast coverage.
- Precipitation is assumed to be uniformly distributed within each forecast interval when splitting rainfall across days.
- Forecast rainfall is an estimate and should not be treated as observed rainfall.

## Intended Use
The daily forecast totals can serve as inputs for the basement flooding prediction pipeline. The current script prints the values to Terminal; it does not yet export them to a CSV file or provide a Python function for other modules to import.