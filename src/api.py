import requests
import json
import configparser
from pathlib import Path

class APIClient:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.endpoint = config.get('API', 'endpoint')


    def fetch_data(self, hex_code: str):
        try:
            response = requests.get(f'{self.endpoint}/{hex_code}')
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