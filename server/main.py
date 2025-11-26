import socket
import threading
import utils.utils as utils

#
def handle_client(client_socket):
    data = client_socket.recv(1024)
    data = data.decode('utf-8')
    methods = utils.Utils()

    if data.startswith("SIGN_UP"):
        email = data.split("'")[1]
        password = data.split("'")[3]
        print(email, password)
        response = methods.handle_signup(email, password)
        if response == "200":
            client_socket.send(f"Sign up was successful!!".encode())
        else:
            client_socket.send(f"There was an error: {response}".encode())

    if data.startswith("LOGIN"):
        email = data.split("'")[1]
        password = data.split("'")[3]
        print(email, password)
        response = methods.handle_login(email, password)
        if response == "200":
            client_socket.send(f"Login was successful!!".encode())
        else:
            client_socket.send(f"There was an error: {response}".encode())

    # print(f"Received from client: {data.decode('utf-8')}")
    # client_socket.sendall(f"Server got from client the things!".encode())
    client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))
server_socket.listen(5)  # Max 5 pending connections

print("Server listening on port 12345...")

while True:
    # make a thread for each client.
    client_socket, addr = server_socket.accept()
    print(f"Accepted connection from {addr}")
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
