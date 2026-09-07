# crashmapqld

WebServer for Fatal Crash Maps in Queensland — a small Flask app that plots the Queensland Government's road-crash dataset on an interactive [Folium](https://python-visualization.github.io/folium/) / Leaflet map, highlighting **fatal** crashes with heat-map, marker, and clustered-marker layers.

## Features

- Interactive map with a toggle between an OpenStreetMap basemap and a black/white ("Stamen Toner") basemap
- **Heat Map** layer showing the density of fatal crashes
- **Fatal Crashes** layer — individual translucent markers; hover to see the death toll, click for the crash nature
- **Clustered Markers** layer — the same crash points grouped into clusters for easier browsing at low zoom
- Layer control so any of the above can be shown/hidden independently
- Simple two-page site: a landing page and the map itself

## Pages / routes

| Route | Description |
|---|---|
| `/` | Home page — short intro to the project and data source, links to the map |
| `/crashmap` | Renders the Folium map with all layers described above |

## Data

The app reads crash records from a `locations.csv` file in the project root at startup. This file is **not included in the repository** (it's listed in `.gitignore`), so it needs to be supplied separately — it's sourced from the [Queensland Government Open Data Portal](https://www.data.qld.gov.au/), which publishes vehicular crash data for the state (fatalities, injuries, and property damage).

At minimum the CSV needs these columns, since `main.py` reads them directly:

- `Crash_Latitude_GDA94`, `Crash_Longitude_GDA94` — crash location
- `Crash_Severity` — only rows equal to `Fatal` are kept
- `Count_Casualty_Fatality` — deaths, shown in the marker tooltip
- `Crash_Nature`, `Crash_Type` — shown in the marker popup
- `Loc_Post_Code` — read in as a string (not parsed as a number)

## Requirements

- Python 3.7
- Flask 1.0.2
- Folium 0.10.0
- pandas 0.23.4

(see `requirements.txt`)

## Running locally

```bash
git clone https://github.com/coolum001/crashmapqld.git
cd crashmapqld
pip install -r requirements.txt

# add locations.csv (Queensland fatal-crash data) to the project root

python main.py
```

Then open http://127.0.0.1:8080 in a browser.

## Deployment

`app.yaml` targets the Google App Engine standard environment (`runtime: python37`), so the app can be deployed with:

```bash
gcloud app deploy
```

## Project structure

```
crashmapqld/
├── main.py              # Flask app: loads crash data, builds the Folium map, defines routes
├── requirements.txt      # Python dependencies
├── app.yaml               # Google App Engine config
├── templates/
│   ├── base.html         # Shared layout (nav menu, footer)
│   ├── index.html        # Home page content
│   └── crashmap.html     # Map page content
└── static/
    └── css/
        └── main.css       # Site styling
```

## Author

Don Cameron — [www.net-analysis.com](http://www.net-analysis.com)

Created by Claude Cowork, and updated 2026 09 07
