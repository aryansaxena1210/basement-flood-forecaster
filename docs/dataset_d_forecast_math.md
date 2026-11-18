# How Dataset D's Simulated Forecast Is Calculated

`src/data/build_dataset_d.py` calculates `rain_tomorrow_forecast_in` from one
number which is the rain that actually fell on the target day (`rain_tomorrow_in`).
It never uses yesterday's or today's rain.

## The rules

Each day follows one rule, chosen by how much rain really fell:

| True rain on the target day | Rule | Forecast |
|---|---|---|
| 0 in (dry) | 10% chance of a false alarm | 0.05 to 0.25 in, otherwise 0 |
| Above 0, under 0.25 in (light) | 15% chance the rain is missed | 0, otherwise use the multiplier |
| 0.25 in or more | Multiplier | True rain times a random factor |

Every forecast is then capped at 6 in and rounded to 2 decimals.

## Chances

For each day the script draws a random number that is between 0 and 1 with every
value being equally likely. A number lands under 0.10 about 10% of the time, so
"number < 0.10" in the code is a 10% chance. Light rain is missed when its number is
under 0.15.

For the false alarm, a false alarm's size comes from another number u, which i between 0 and 1:

    false alarm = 0.05 + 0.20 x u

so u = 0 gives 0.05 in, u = 1 gives 0.25 in.

## The multiplier

    forecast = true rain x e^(0.5 x z)

z is a random number from a bell curve that has an average of 0 and standard deviation of 1, and is
limited to between -2 and +2. Small misses are common and big misses are rare.

| z | Multiplier | 2.00 in of true rain becomes |
|---|---|---|
| -2 | 0.37 | 0.74 in |
| -1 | 0.61 | 1.21 in |
| 0 | 1.00 | 2.00 in |
| +1 | 1.65 | 3.30 in |
| +2 | 2.72 | 5.44 in |

About two-thirds of days have z between -1 and +1, so the forecast is
usually 40% too low to 65% too high. Too high and too low are equally
likely, and the forecast is never negative. 0.5 sets the size of the
errors meaning a larger value means bigger misses.

## Random numbers

The random numbers are seeded with 5730 plus the target date (for example
`5730-2023-07-05`). The same seed always gives the same numbers, so the
file is identical every run, and each day's numbers are independent of
every other day.

## Examples (2023)

- Jul 5: true rain 1.76 in, z = -1.02. Multiplier e^(-0.51) = 0.60, so
  1.76 x 0.60 = 1.06 in.
- Jul 9: dry. False-alarm number 0.041 is under 0.10, and u = 0.309, so
  0.05 + 0.20 x 0.309 = 0.11 in.
- Jul 2: true rain 4.68 in, z = +0.89. 4.68 x 1.56 = 7.29 in, capped at
  6.00 in.

## Settings

All are set at the top of the script, and all are assumptions rather than
measurements. There are no past forecasts that are saved to measure against,
so these are all educated guesses.

| Setting | Value | Meaning |
|---|---|---|
| `FALSE_ALARM_CHANCE` | 0.10 | Share of dry days given a false alarm |
| `FALSE_ALARM_MIN_IN`, `FALSE_ALARM_MAX_IN` | 0.05, 0.25 | Size range of a false alarm |
| `MISS_CHANCE` | 0.15 | Share of light-rain days forecast as dry |
| `LIGHT_RAIN_IN` | 0.25 | Upper limit of light rain |
| `AMOUNT_SPREAD` | 0.5 | Size of amount errors |
| `MAX_AMOUNT_DRAW` | 2.0 | Limit on z |
| `MAX_FORECAST_IN` | 6.0 | Largest forecast allowed |
| `RANDOM_SEED` | 5730 | Starting point for the random numbers |
