import socket
import configparser

class NetworkStreamer:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.host = config.get('NetworkStreamer', 'adsb_host')
        self.port = int(config.get('NetworkStreamer', 'adsb_port'))
        self.lines_to_fetch = int(config.get('NetworkStreamer', 'lines_to_fetch'))


    def fetch_data(self) -> set:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        i = 0
        results = set()
        try:
            while i < self.lines_to_fetch:
                data = s.recv(1024)
                if not data:
                    break
                csv_line = data.decode('utf-8')
                csv_list = csv_line.split(',')
                hex_code = csv_list[4]
                results.add(hex_code)
                i = i + 1
        finally:
            s.close()

        return results

    
    def fetch_test_data(self) -> list:
        return list(('780AAB', '4CA24E', '3C65D5'))
