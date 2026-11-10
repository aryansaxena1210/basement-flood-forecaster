import requests
from pathlib import Path
from datetime import date

# NOAA API URL
BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"

# Create the output folder
OUTPUT_FOLDER = Path("data/raw/noaa")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# NOAA weather stations
stations = {
	"USW00094846": "ohare_2018_now.csv",
	"USW00014819": "midway_2018_now.csv",
}

# Download rainfall data for each station
for station_id, filename in stations.items():
	# Parameters for the NOAA request
	parameters = {
    "dataset": "daily-summaries",
    "stations": station_id,
    "startDate": "2018-01-01",
    "endDate": date.today().isoformat(),
    "dataTypes": "PRCP",
    "units": "standard",
    "format": "csv"
}

	# Send request to NOAA
	response = requests.get(BASE_URL, params=parameters)

	# Check whether the request was successful
	response.raise_for_status()

	# Save downloaded data
	output_path = OUTPUT_FOLDER / filename
	with open(output_path, "w", encoding="utf-8") as file:
		file.write(response.text)

	print(f"Downloaded: {output_path}")
