import os
import time
from src.api import APIClient
from src.db import DatabaseManager
from src.network_stream import NetworkStreamer

if __name__ == "__main__":
    ns = NetworkStreamer()
    api = APIClient()
    dm = DatabaseManager(os.environ['ADSB_DB_PASSWORD'])
    while True:
        adsb_data = ns.fetch_data()
        callsigns_by_hex = ns.fetch_callsigns_by_hex()
        for hex_code in adsb_data:
            print(f"Processing hex code: {hex_code}")
            data = api.fetch_data(hex_code)
            if data is not None:
                if dm.is_there_a_recent_record(hex_code):
                    print(f"Aircraft with hex code {hex_code} has been observed recently. Not inserting a new record")
                else:
                    callsign = callsigns_by_hex.get(hex_code.upper())
                    route_data = api.fetch_route_by_callsign(callsign) if callsign else api.fetch_route_by_callsign('')
                    dm.insert_record(data, hex_code, route_data)
            time.sleep(1)
