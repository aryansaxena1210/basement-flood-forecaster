# Flood Rule: What Counts as a Flood

This is the one place that records how we decided what a "flood" is and how the rain input is built. If a decision here changes, change it here first, then tell the people who use it.

## The decisions

| # | Decision | Why |
|---|---|---|
| 1 | **Flood day:** a day with **100 or more** complaints | A normal day is about 8 (median). 100 is about 12x that and the top ~3% of days. A cutoff of 50 gave 62 events, mostly noise. There is no natural break in the data, so this is a judgment call. |
| 2 | **`daily.csv` starts on 2019-03-01**, not 2019-01-01 | The 311 category was still ramping up. Jan and Feb 2019 had a median of 0 to 1 complaints a day and 36 zero-complaint days. |
| 3 | **Event:** flood days at most 2 days apart (at most one quiet day between them) are merged into one event | One storm often has a dip day in the middle (May 16, 2020 had 31 complaints between days of 275 and 675). Splitting one storm into two double counts it, and the second half looks like a flood with no rain behind it. Wrongly merging two storms is the cheaper mistake. When unsure, merge. |
| 4 | **Big event:** the busiest single day had **500 or more** complaints | Gives 6 events. Round number, not a natural break. We score big and small floods separately because the huge 2023 and 2025 floods would otherwise swamp the average. |
| 5 | **An event is dated by its peak day** (busiest day), not its first day | Merging can chain small flood days onto a big flood. The Aug 2025 event "starts" on Aug 12, but the real flood is Aug 17. |
| 6 | **Rain input is the larger of the O'Hare and Midway daily totals** | A storm can hit one airport and miss the other. On Jul 25, 2025 O'Hare read 0.01 in and Midway 3.25 in; an average would halve it. Scores with average and max were nearly equal (rank correlation 0.35 over 3 days). If one station is blank, use the other. |
| 7 | **Person 1 checks every event** against rain and news and marks it `yes`, `unsure`, or `no`. A `no` stays in the file but is left out when scoring models. | The list is built from complaint counts, which is also the thing we predict. A spike with no storm behind it (a sewer break, a system glitch) could be labeled a flood. A second source catches that. |

**Tabled:** using Water On Street complaints as a second storm signal for Person 1's check. Revisit when the event list is ready.

## Where this lives in the code

- `src/data/flood_events.py` holds the cutoff (100), the merge gap (2) and the big-event threshold (500), and finds the events.
- `src/data/build_daily.py` uses it to set `is_spike` in `daily.csv`.
- Decision 5 (peak day) is decided but not applied anywhere yet. The code returns each event's flood days, and the peak day is the busiest one.

## Event list

`data/labels/flood_events.csv`, one row per event. Not generated yet. Person 2 produces the draft by Fri, Oct 30. Person 1 fills in the last two columns by Fri, Nov 6.

| Column | Filled by | Meaning |
|---|---|---|
| `event_id` | Person 2 | 1, 2, 3... |
| `start_date`, `end_date` | Person 2 | First and last flood day |
| `peak_date`, `peak_count` | Person 2 | Busiest day and its complaint count |
| `total_complaints` | Person 2 | Sum over the event's days |
| `big` | Person 2 | `yes` if `peak_count` is 500 or more |
| `confirmed` | Person 1 | `yes`, `unsure`, or `no` |
| `notes` | Person 1 | Rain total and a source link, or why they chose `no` |

## Known weak spots

- 2024's only event is a single day with 101 complaints, a hair over the cutoff. 2024 is a fragile test year.
- Several events are single winter days (Feb 2022 twice, Jan 2025, Jan and Mar 2026). They may not be rain related. Person 1's check is for these.
- Complaints stay high for 13 to 20 days after the biggest floods, so one event can be long (Jul 2023 runs 18 days).
