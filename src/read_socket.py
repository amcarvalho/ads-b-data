import socket

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the host and the port
host = 'localhost'
port = 30003

# Connect to the server
s.connect((host, port))

i = 0

# Read lines from the socket
try:
    while i <= 10:
        # Receive data from the server
        data = s.recv(1024)
        if not data:
            break
        # Decode the data and print it
        print(data.decode('utf-8'))
        i = i + 1
finally:
    # Close the connection
    s.close()
