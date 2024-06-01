import requests
import json
from pathlib import Path

class APIClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def fetch_data(self, hex_code: str):
        response = requests.get(f'{self.endpoint}/{hex_code}')
        if response.status_code == 200:
            return response.json()
        else:
            print(f'API call failed with status code: {response.status_code}')
            return None
    
    def fetch_test_data(self):
        file_path = Path('./resources/example.json')
        file_content = file_path.read_text()
        return json.loads(file_content)