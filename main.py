from src.api import APIClient
from src.db import DatabaseManager

api = APIClient('dummy_url')
data = api.fetch_test_data()

dm = DatabaseManager('adsb_data', 'adsb_user', 'adsb_password', '127.0.0.1')
dm.insert_record(data, 'test_id')