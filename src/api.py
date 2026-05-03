import requests
import json
import configparser
from pathlib import Path
from typing import Dict, Optional

class APIClient:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.endpoint = config.get('API', 'endpoint')
        self.callsign_route_endpoint = config.get('API', 'callsign_route_endpoint')
        self.api_timeout_seconds = int(config.get('API', 'timeout_seconds', fallback='10'))


    def fetch_data(self, hex_code: str):
        try:
            response = requests.get(f'{self.endpoint}/{hex_code}', timeout=self.api_timeout_seconds)
            if response.status_code == 200:
                response_json = response.json()
                return response_json['response']['aircraft']
            else:
                print(f'API call failed with status code: {response.status_code}')
                return None
        except:
            print("Failed to fetch data")
            return None

    
    def fetch_test_data(self):
        file_path = Path('./resources/example.json')
        file_content = file_path.read_text()
        return json.loads(file_content)


    def fetch_route_by_callsign(self, callsign: str) -> Dict[str, Optional[str]]:
        if not callsign:
            return self._empty_route_fields()
        try:
            response = requests.get(
                f'{self.callsign_route_endpoint}/{callsign}',
                timeout=self.api_timeout_seconds,
            )
            if response.status_code == 404:
                return self._empty_route_fields()
            if response.status_code != 200:
                print(f'Callsign route API call failed with status code: {response.status_code}')
                return self._empty_route_fields()

            response_json = response.json()
            flightroute = response_json.get('response', {}).get('flightroute')
            if not flightroute:
                return self._empty_route_fields()

            origin = flightroute.get('origin') or {}
            destination = flightroute.get('destination') or {}
            return {
                'departure_airport_code': origin.get('icao_code') or origin.get('iata_code'),
                'departure_airport_city': origin.get('municipality'),
                'departure_airport_country': origin.get('country_name'),
                'arrival_airport_code': destination.get('icao_code') or destination.get('iata_code'),
                'arrival_airport_city': destination.get('municipality'),
                'arrival_airport_country': destination.get('country_name'),
            }
        except Exception:
            print('Failed to fetch route by callsign')
            return self._empty_route_fields()


    def _empty_route_fields(self) -> Dict[str, Optional[str]]:
        return {
            'departure_airport_code': None,
            'departure_airport_city': None,
            'departure_airport_country': None,
            'arrival_airport_code': None,
            'arrival_airport_city': None,
            'arrival_airport_country': None,
        }