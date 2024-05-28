import socket

class NetworkStreamer:
    def __init__(self, host='localhost', port=30003):
        self.host = host
        self.port = port

    def fetch_data(self, lines_to_fetch=100):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        i = 0
        results = list()
        try:
            while i < lines_to_fetch:
                data = s.recv(1024)
                if not data:
                    break
                csv_line = data.decode('utf-8')
                csv_list = csv_line.split(',')
                hex_code = csv_list[4]
                results.append(hex_code)
                i = i + 1
        finally:
            s.close()

        return results

    
    def fetch_test_data(self):
        file_path = Path('./resources/example.json')
        file_content = file_path.read_text()
        return json.loads(file_content)
