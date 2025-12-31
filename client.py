import socket

HOST = "localhost"
PORT = 12345

class Client:
    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.connect((HOST, PORT))

    def send(self, msg):
        self.tcp.send(msg.encode())
        return self.tcp.recv(4096).decode()
