import os
from src.api import APIClient
from src.db import DatabaseManager
from src.network_stream import NetworkStreamer

if __name__ == "__main__":
    ns = NetworkStreamer()
    api = APIClient()
    dm = DatabaseManager(os.environ['ADSB_DB_PASSWORD'])
    while True:
        adsb_data = ns.fetch_data()
        for hex_code in adsb_data:
            print(f"Processing hex code: {hex_code}")
            data = api.fetch_data(hex_code)
            if dm.is_there_a_recent_record(hex_code):
                print(f"Aircraft with hex code {hex_code} has been observed recently. Not inserting a new record")
            else:
                dm.insert_record(data, hex_code)


# api = APIClient('dummy_url')
# data = api.fetch_test_data()
# ns = NetworkStreamer()


# dm = DatabaseManager('adsb_password')
# print(dm.is_there_a_recent_record('test_id2'))
# dm.insert_record(data, 'test_id2')
# print(ns.fetch_data())
# print(ns.fetch_test_data())