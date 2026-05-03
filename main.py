import logging
import os
import time
import configparser

from src.api import APIClient
from src.db import DatabaseManager
from src.network_stream import NetworkStreamer

logger = logging.getLogger(__name__)


def _configure_logging():
    config = configparser.ConfigParser()
    config.read('config.ini')
    level_name = os.environ.get(
        'ADSB_LOG_LEVEL',
        config.get('General', 'log_level', fallback='INFO'),
    ).upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )


if __name__ == "__main__":
    _configure_logging()
    ns = NetworkStreamer()
    api = APIClient()
    dm = DatabaseManager(os.environ['ADSB_DB_PASSWORD'])
    while True:
        adsb_data = ns.fetch_data()
        callsigns_by_hex = ns.fetch_callsigns_by_hex()
        logger.info(
            'Batch: %d hex codes from stream, %d with callsign from feeder',
            len(adsb_data),
            len(callsigns_by_hex),
        )
        skipped_recent = 0
        inserted = 0
        inserted_with_route = 0
        for hex_code in adsb_data:
            print(f"Processing hex code: {hex_code}")
            data = api.fetch_data(hex_code)
            if data is not None:
                if dm.is_there_a_recent_record(hex_code):
                    skipped_recent += 1
                    print(f"Aircraft with hex code {hex_code} has been observed recently. Not inserting a new record")
                else:
                    callsign = callsigns_by_hex.get(hex_code.upper())
                    if callsign:
                        route_data = api.fetch_route_by_callsign(callsign)
                    else:
                        route_data = api.fetch_route_by_callsign('')
                        logger.debug('No feeder callsign for hex %s', hex_code)
                    if route_data.get('departure_airport_code') or route_data.get('arrival_airport_code'):
                        inserted_with_route += 1
                    dm.insert_record(data, hex_code, route_data)
                    inserted += 1
                    logger.debug(
                        'Inserted hex=%s callsign=%r dep=%s arr=%s',
                        hex_code,
                        callsign,
                        route_data.get('departure_airport_code'),
                        route_data.get('arrival_airport_code'),
                    )
            time.sleep(1)
        if inserted or skipped_recent:
            logger.info(
                'Cycle summary: inserted=%d (with route fields=%d), skipped_recent=%d',
                inserted,
                inserted_with_route,
                skipped_recent,
            )
