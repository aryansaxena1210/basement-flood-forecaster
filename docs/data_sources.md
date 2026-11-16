# Data Sources: Where the Data Comes From

Three public APIs, no keys needed. All three calls below were tested on 2026-10-23. Paste any URL into a browser to see what it returns.

| What | Source | Used for |
|---|---|---|
| Basement-flooding complaints | Chicago 311 (Socrata) | The number we predict |
| Daily rain | NOAA NCEI | Training inputs |
| Rain forecast | National Weather Service | Live inputs |

## 1. Chicago 311 complaints

Base URL: `https://data.cityofchicago.org/resource/v6vf-nfxy.json`

Filter on `sr_type='Water in Basement Complaint'`.

**Look at a few raw rows**
```
https://data.cityofchicago.org/resource/v6vf-nfxy.json?$where=sr_type='Water%20in%20Basement%20Complaint'&$limit=2
```

**Daily counts, 2018 to now, duplicates removed** (this is what builds our target column)
```
https://data.cityofchicago.org/resource/v6vf-nfxy.json?$select=date_trunc_ymd(created_date)%20as%20day,count(*)%20as%20n&$where=sr_type='Water%20in%20Basement%20Complaint'%20AND%20created_date>='2018-01-01T00:00:00'%20AND%20duplicate=false&$group=day&$order=day&$limit=5000
```

Result looks like:
```json
[{"day":"2023-07-02T00:00:00.000","n":"1337"}, ...]
```

**Same call with curl (PowerShell, use `curl.exe`)**
```
curl.exe -G "https://data.cityofchicago.org/resource/v6vf-nfxy.json" `
  --data-urlencode "`$select=date_trunc_ymd(created_date) as day, count(*) as n" `
  --data-urlencode "`$where=sr_type='Water in Basement Complaint' AND created_date>='2018-01-01T00:00:00' AND duplicate=false" `
  --data-urlencode "`$group=day" --data-urlencode "`$order=day" --data-urlencode "`$limit=5000" `
  -o data/raw/311/daily_counts_2018_now.json
```
In bash, drop the backticks and use `\$select` instead of `` `$select ``.

**Good to know**
- The category starts on **2018-12-19**, not January 2018. About 70,500 complaints in total.
- About 4.5% of rows are marked `duplicate=true`. We filter them out with `duplicate=false`.
- Days with zero complaints are not in the result. Fill them in with 0 when building `daily.csv`.
- Socrata returns 1,000 rows unless you set `$limit`. Counts come back as strings (`"1337"`), so convert them to numbers.
- Dates are in Chicago local time.

## 2. NOAA daily rain

Base URL: `https://www.ncei.noaa.gov/access/services/data/v1`

Two stations, because they can disagree a lot (July 2, 2023: O'Hare 3.35 in, Midway 4.68 in):

| Station | ID |
|---|---|
| O'Hare | `USW00094846` |
| Midway | `USW00014819` |

**A few days (JSON), good for a quick look**
```
https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00094846&startDate=2023-07-01&endDate=2023-07-05&dataTypes=PRCP&units=standard&format=json
```
```json
[{"DATE":"2023-07-02","STATION":"USW00094846","PRCP":"3.35"}, ...]
```

**Full history (CSV)**
```
https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00094846&startDate=2018-01-01&endDate=2026-10-22&dataTypes=PRCP&units=standard&format=csv
```
```
curl.exe -o data/raw/noaa/ohare_2018_now.csv "<the URL above>"
```
Swap the station ID for Midway.

**Good to know**
- `PRCP` is rain in inches per day (we asked for `units=standard`).
- 2018-01-01 to 2026-10-20: every day has a row. O'Hare has no blank rain values. Midway has 4 blank days. We use the larger of the two (a storm can hit one airport and miss the other). When one is blank we use the other.
- This only gives daily totals. We are not using an hourly rain rate.
- The most recent day or two may not be posted yet.

## 3. NWS rain forecast

NWS needs a `User-Agent` header. Any short string that says who you are works.

**Step 1: find the forecast grid for a point** (O'Hare)
```
https://api.weather.gov/points/41.9742,-87.9073
```
It returns `gridId: "LOT"`, `gridX: 66`, `gridY: 77`, plus links to the forecasts.

**Step 2: get the raw forecast grid, including forecast rain amounts**
```
https://api.weather.gov/gridpoints/LOT/66,77
```
```
curl.exe -H "User-Agent: coms5730-class-project" "https://api.weather.gov/gridpoints/LOT/66,77"
```

The part we want is `properties.quantitativePrecipitation.values`:
```json
{"validTime":"2026-10-24T06:00:00+00:00/PT6H","value":0}
```
Each entry is a time block (`PT6H` = 6 hours, `P1D` = 1 day) and the **millimeters** of rain forecast in it. Convert to inches by dividing by 25.4.

`properties.probabilityOfPrecipitation` has the chance of rain in the same format.

**Good to know**
- It covers about 2.5 days ahead and is updated about hourly.
- On the day we tested it was dry, so every value was 0. We haven't yet seen it with a real storm in it.
- The NWS forecast starts from now, so it can't be used for training. It's only for the live tool.
- `/gridpoints/LOT/66,77/forecast` gives text forecasts for people to read. We don't use it.

## Where the downloaded files go

`data/raw/`. That folder is not in git, so every file in it must be recreatable from the calls above. Whoever builds `src/data` should turn these calls into a script.
