# ADS-B Data Collector

This service ingests aircraft hex codes from your ADS-B receiver stream, enriches aircraft metadata using ADSBDB, resolves route details by callsign, and stores records in PostgreSQL.

## Route enrichment behavior

- Callsign is fetched from your feeder endpoint (`/data/aircraft.json`) and matched by hex code.
- Route data is fetched from `https://api.adsbdb.com/v0/callsign/{CALLSIGN}`.
- If route lookup fails, is missing, or returns unknown callsign, records are still inserted with route fields set to `NULL`.

## Configuration

Update `config.ini`:

- `[API].endpoint` for aircraft lookup
- `[API].callsign_route_endpoint` for route lookup
- `[NetworkStreamer].feeder_aircraft_url` for your feeder JSON endpoint

Set DB password in your shell:

- `export ADSB_DB_PASSWORD='<your_db_password>'`

## Database setup

Fresh setup:

- `psql -f resources/db_config.sql`

Existing DB migration:

- `psql -d adsb_data -f resources/migrations/001_add_route_columns.sql`

## Run

1. Create and activate a virtual environment:
   - `python3 -m venv .venv`
2. Install dependencies:
   - `.venv/bin/pip install -r requirements.txt`
3. Start service:
   - `.venv/bin/python main.py`
# ADS-B Data Collector

This project ingests aircraft hex codes from a local ADS-B receiver feed, enriches aircraft details from ADSBDB, optionally enriches route airport details from FR24, and stores records in PostgreSQL.

## Prerequisites

- Python 3.9+ (recommended for this repo)
- PostgreSQL
- A receiver streaming ADS-B messages to `localhost:30003` (or adjust `config.ini`)

## Configuration

1. Set DB password:
   - `export ADSB_DB_PASSWORD='<your_db_password>'`
2. Set FR24 API token:
   - `export FR24_API_TOKEN='<your_fr24_token>'`
   - You can also set `token` under `[FR24]` in `config.ini`.
3. Check `config.ini` values for:
   - `[API].endpoint`
   - `[FR24]` endpoint settings
   - `[NetworkStreamer]` receiver host/port

## Database setup

For a fresh setup, run:

- `psql -f resources/db_config.sql`

For existing databases, run migration:

- `psql -d adsb_data -f resources/migrations/001_add_fr24_airport_columns.sql`

## Run

Install dependencies in a virtual environment:

- `python3 -m venv .venv`
- `.venv/bin/pip install requests psycopg2-binary`

Run ingestion:

- `.venv/bin/python main.py`

## Behavior with FR24 enrichment

- The pipeline first calls ADSBDB with the receiver hex code.
- If ADSBDB returns aircraft data and record is not recent, it tries FR24 enrichment using the ADSBDB registration.
- If FR24 succeeds, it stores:
  - departure airport code, city, country
  - arrival airport code, city, country
- If FR24 fails or returns no result, it still inserts the ADSBDB data with those 6 columns as `NULL`.
