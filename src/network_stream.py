import socket
import configparser
import time

class NetworkStreamer:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.host = config.get('NetworkStreamer', 'adsb_host')
        self.port = int(config.get('NetworkStreamer', 'adsb_port'))
        self.lines_to_fetch = int(config.get('NetworkStreamer', 'lines_to_fetch'))


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
                    hex_code = csv_list[4]
                    results.add(hex_code)
                    i = i + 1
                except IndexError:
                    print("Skipping invalid record ...")
        finally:
            s.close()

        return results

    
    def fetch_test_data(self) -> list:
        return list(('780AAB', '4CA24E', '3C65D5'))
