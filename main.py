import logging
import os
import time
import configparser
from typing import Dict, Optional

from src.adsb_normalize import normalize_mode_s_hex
from src.api import APIClient
from src.db import DatabaseManager
from src.network_stream import NetworkStreamer

logger = logging.getLogger(__name__)
STRICT_ROUTE_ENRICHMENT = os.environ.get('ADSB_STRICT_ROUTE_ENRICHMENT', 'true').lower() == 'true'
EMPTY_ROUTE_FIELDS = {
    'departure_airport_code': None,
    'departure_airport_city': None,
    'departure_airport_country': None,
    'arrival_airport_code': None,
    'arrival_airport_city': None,
    'arrival_airport_country': None,
}


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


def _is_icao_code(value: Optional[str]) -> bool:
    if not value:
        return False
    code = value.strip().upper()
    return len(code) == 4 and code.isalpha()


def _is_route_confident(data: Dict, callsign: str, route_data: Dict[str, Optional[str]]) -> bool:
    # Conservative gate: prefer NULL over a potentially wrong route.
    if not callsign:
        return False
    if not (_is_icao_code(route_data.get('departure_airport_code')) and _is_icao_code(route_data.get('arrival_airport_code'))):
        return False
    operator = (data.get('registered_owner_operator_flag_code') or '').strip().upper()
    if operator and not callsign.startswith(operator):
        return False
    return True


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
            hex_key = normalize_mode_s_hex(hex_code)
            print(f"Processing hex code: {hex_key}")
            data = api.fetch_data(hex_key)
            if data is not None:
                if dm.is_there_a_recent_record(hex_key):
                    skipped_recent += 1
                    print(f"Aircraft with hex code {hex_key} has been observed recently. Not inserting a new record")
                else:
                    callsign = callsigns_by_hex.get(hex_key)
                    if callsign:
                        route_data = api.fetch_route_by_callsign(callsign)
                    else:
                        route_data = api.fetch_route_by_callsign('')
                        logger.debug('No feeder callsign for hex %s', hex_key)
                    if STRICT_ROUTE_ENRICHMENT and not _is_route_confident(data, callsign or '', route_data):
                        logger.info(
                            'Dropping low-confidence route: hex=%s callsign=%r dep=%r arr=%r',
                            hex_key,
                            callsign,
                            route_data.get('departure_airport_code'),
                            route_data.get('arrival_airport_code'),
                        )
                        route_data = EMPTY_ROUTE_FIELDS.copy()
                    if route_data.get('departure_airport_code') or route_data.get('arrival_airport_code'):
                        inserted_with_route += 1
                    else:
                        if callsign:
                            logger.info(
                                'Insert without route from ADSBDB: hex=%s callsign=%r',
                                hex_key,
                                callsign,
                            )
                        else:
                            logger.info(
                                'Insert without route (no feeder callsign): hex=%s',
                                hex_key,
                            )
                    dm.insert_record(data, hex_key, route_data)
                    inserted += 1
                    logger.debug(
                        'Inserted hex=%s callsign=%r dep=%s arr=%s',
                        hex_key,
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
