# Aire Santiago: PM2.5 Air Quality Explorer

Interactive dashboard exploring PM2.5 air quality patterns across Santiago's
monitoring stations using data from SINCA, Chile's national air quality network.

**Live app:** [aire-santiago.streamlit.app](https://aire-santiago.streamlit.app)

## What this project does

Analyses six years of hourly PM2.5 data (2020–2025) from 11 monitoring stations
in Santiago's Región Metropolitana, cleaning and aggregating it into daily averages
and presenting the results in an interactive three-tab dashboard.

## Key findings

- PM2.5 peaks every winter (June–August) due to temperature inversions that trap
  pollution in Santiago's basin geography. Summer values are consistently low.
- El Bosque, Cerro Navia, and Cerrillos II record the highest mean PM2.5
  (~26–27 µg/m³), all peripheral comunas with higher poverty rates.
- Las Condes records the lowest mean PM2.5 (~18 µg/m³), consistent with its
  location on the eastern edge of the city and its socioeconomic profile.
- 9.1% of station-days exceeded Chile's legal standard of 50 µg/m³, with the
  worst stations exceeding the norm on roughly one in every six to eight days
  during winter months.
- A general downward trend in PM2.5 is visible from 2021 onwards across most
  stations, with 2020 showing a notable dip consistent with COVID-19 lockdowns.

## Dashboard features

- **Tendencia:** time-series chart with 7-day rolling average, exceedance markers,
  and summary metrics. Optional two-station comparison mode.
- **Estacionalidad:** monthly PM2.5 averages with winter highlight for the
  selected station.
- **Comparación:** cross-station ranking with data coverage notes.

## Data sources

- [SINCA](https://sinca.mma.gob.cl) — hourly PM2.5 readings from 11 RM
  monitoring stations (2020–2025), Ministerio del Medio Ambiente, Chile.

## Project structure
portfolio-airquality-santiago/
├── notebooks/
│ ├── 01_ingest.ipynb # Load and combine SINCA CSV files
│ ├── 02_clean.ipynb # Aggregate to daily, quality filter
│ ├── 03_analysis.ipynb # Seasonal patterns, station comparison
│ └── 04_forecast.ipynb # Rolling average and linear trend model
├── data/
│ └── interim/ # Cleaned parquet files
├── figures/ # Saved chart images
├── app.py # Streamlit dashboard
└── requirements.txt

## How to run locally

```bash
git clone https://github.com/ruthsepulveda/portfolio-airquality-santiago
cd portfolio-airquality-santiago
python -m venv air-santiago
air-santiago\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Tools

Python · pandas · Plotly · Streamlit · scikit-learn · SINCA

