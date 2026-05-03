import logging
import socket
import configparser
import time
import requests

from src.adsb_normalize import normalize_callsign, normalize_mode_s_hex

logger = logging.getLogger(__name__)


class NetworkStreamer:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.host = config.get('NetworkStreamer', 'adsb_host')
        self.port = int(config.get('NetworkStreamer', 'adsb_port'))
        self.lines_to_fetch = int(config.get('NetworkStreamer', 'lines_to_fetch'))
        self.feeder_aircraft_url = config.get('NetworkStreamer', 'feeder_aircraft_url', fallback='')
        self.feeder_timeout_seconds = int(config.get('NetworkStreamer', 'feeder_timeout_seconds', fallback='10'))


    def fetch_data(self) -> set:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # keep trying to connect until successful
        while True:
            try:
                s.connect((self.host, self.port))
                break
            except ConnectionRefusedError:
                print(f"Connection to {self.host}:{self.port} refused, retrying in 60s...")
                time.sleep(60)
        i = 0
        results = set()
        try:
            while i < self.lines_to_fetch:
                data = s.recv(1024)
                if not data:
                    break
                csv_line = data.decode('utf-8')
                csv_list = csv_line.split(',')
                try:
                    raw_hex = csv_list[4]
                    hex_code = normalize_mode_s_hex(raw_hex)
                    if hex_code:
                        results.add(hex_code)
                    i = i + 1
                except IndexError:
                    print("Skipping invalid record ...")
        finally:
            s.close()

        return results

    
    def fetch_test_data(self) -> list:
        return list(('780AAB', '4CA24E', '3C65D5'))


    def fetch_callsigns_by_hex(self) -> dict:
        if not self.feeder_aircraft_url:
            return {}
        try:
            response = requests.get(self.feeder_aircraft_url, timeout=self.feeder_timeout_seconds)
            if response.status_code != 200:
                print(f"Feeder API call failed with status code: {response.status_code}")
                return {}
            payload = response.json()
            aircraft = payload.get('aircraft', [])
            callsigns_by_hex = {}
            for entry in aircraft:
                hex_code = normalize_mode_s_hex(entry.get('hex') or '')
                raw_cs = entry.get('flight') or entry.get('callsign') or ''
                callsign = normalize_callsign(raw_cs)
                if hex_code and callsign:
                    callsigns_by_hex[hex_code] = callsign
            logger.info(
                'Feeder aircraft.json: %d entries, %d with hex+flight',
                len(aircraft),
                len(callsigns_by_hex),
            )
            return callsigns_by_hex
        except Exception:
            logger.exception('Failed to fetch callsigns from feeder endpoint')
            return {}
